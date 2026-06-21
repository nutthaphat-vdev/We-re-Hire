# We're Hired v1.1 — 2026-05-27 build2
"""
WeHire — Daily Wage Matchmaking Platform
main.py — FastAPI entry point + Auth + Profile CRUD + Matching engine

Stack: FastAPI + asyncpg + Supabase (PostgreSQL + PostGIS) + PyJWT
"""

import os
import logging
import asyncpg
import jwt

logger = logging.getLogger("wehire")
import bcrypt
import httpx
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, Header, Request, status, File, UploadFile
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import BaseSettings

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    database_url:         str
    jwt_secret:           str
    jwt_algorithm:        str = "HS256"
    jwt_expire_minutes:   int = 120
    cors_origins:         str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000,null"
    frontend_url:         str = ""   # Railway frontend URL เช่น https://wehire.up.railway.app
    supabase_url:         str = "https://wexupoegrynxbhdzioym.supabase.co"
    supabase_anon_key:    str = ""
    supabase_jwt_secret:  str = ""  # Settings → API → JWT Secret
    supabase_service_key: str = ""  # Settings → API → service_role key (สำหรับ Storage)
    admin_secret:         str = ""  # X-Admin-Secret header สำหรับ admin endpoints

    class Config:
        env_file = ".env"

settings = Settings()


# ---------------------------------------------------------------------------
# DB Connection Pool (lifespan)
# ---------------------------------------------------------------------------

pool: asyncpg.Pool | None = None


async def auto_verify_completed_jobs():
    """Cron ทุก 30 นาที: auto-verify หรือ disputed งานที่ employer ไม่ยืนยันภายใน 2 ชม."""
    if pool is None:
        return
    try:
        async with pool.acquire() as db:
            # ── Case 1: duration ≥ 90% → auto-verify ──────────────────────────
            verified_rows = await db.fetch(
                """
                SELECT
                    ja.id,
                    jp.id           AS job_id,
                    jp.title        AS job_title,
                    wp.user_id      AS worker_user_id,
                    ep.user_id      AS employer_user_id
                FROM   job_applications ja
                JOIN   job_postings      jp ON jp.id  = ja.job_id
                JOIN   employer_profiles ep ON ep.id  = jp.employer_id
                JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
                WHERE  ja.status          = 'completed'
                  AND  ja.work_ended_at  IS NOT NULL
                  AND  ja.work_started_at IS NOT NULL
                  AND  NOW() - ja.work_ended_at >= INTERVAL '2 hours'
                  AND  (
                    jp.work_start IS NULL
                    OR jp.work_end IS NULL
                    OR EXTRACT(EPOCH FROM (ja.work_ended_at - ja.work_started_at)) >=
                       0.9 * (
                         CASE WHEN jp.work_end >= jp.work_start
                              THEN EXTRACT(EPOCH FROM (jp.work_end - jp.work_start))
                              ELSE EXTRACT(EPOCH FROM (jp.work_end - jp.work_start)) + 86400
                         END
                       )
                  )
                """
            )
            for row in verified_rows:
                await db.execute(
                    "UPDATE job_applications SET status='verified', employer_verified_at=NOW() WHERE id=$1",
                    row["id"],
                )
                # behavioral score: jobs_completed + 1
                await db.execute(
                    "UPDATE worker_profiles SET jobs_completed = jobs_completed + 1 WHERE user_id = $1",
                    row["worker_user_id"],
                )
                await _recompute_reliability(db, row["worker_user_id"])
                # ถ้า slots เต็มแล้ว → mark job เป็น filled
                await db.execute(
                    """
                    UPDATE job_postings SET status='filled'
                    WHERE  id=$1 AND status='open'
                      AND  slots_filled >= slots_available
                    """,
                    row["job_id"],
                )
                msg = f"งาน {row['job_title']} ได้รับการยืนยันอัตโนมัติ (2 ชม. หลังงานเสร็จ) กรุณาให้คะแนนและรีวิว"
                await db.execute(
                    "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'review_pending', '⭐ ให้คะแนนงาน', $2)",
                    row["worker_user_id"], msg,
                )
                await db.execute(
                    "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'review_pending', '⭐ ให้คะแนน Worker', $2)",
                    row["employer_user_id"], msg,
                )
                logger.info(f"[auto_verify] auto-verified application {row['id']}")

            # ── Case 2: duration < 90% → disputed (ส่ง admin ตัดสิน) ─────────
            disputed_rows = await db.fetch(
                """
                SELECT
                    ja.id,
                    jp.title        AS job_title,
                    wp.user_id      AS worker_user_id,
                    ep.user_id      AS employer_user_id
                FROM   job_applications ja
                JOIN   job_postings      jp ON jp.id  = ja.job_id
                JOIN   employer_profiles ep ON ep.id  = jp.employer_id
                JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
                WHERE  ja.status          = 'completed'
                  AND  ja.work_ended_at  IS NOT NULL
                  AND  ja.work_started_at IS NOT NULL
                  AND  NOW() - ja.work_ended_at >= INTERVAL '2 hours'
                  AND  jp.work_start IS NOT NULL
                  AND  jp.work_end   IS NOT NULL
                  AND  EXTRACT(EPOCH FROM (ja.work_ended_at - ja.work_started_at)) <
                       0.9 * (
                         CASE WHEN jp.work_end >= jp.work_start
                              THEN EXTRACT(EPOCH FROM (jp.work_end - jp.work_start))
                              ELSE EXTRACT(EPOCH FROM (jp.work_end - jp.work_start)) + 86400
                         END
                       )
                """
            )
            for row in disputed_rows:
                await db.execute(
                    "UPDATE job_applications SET status='disputed' WHERE id=$1",
                    row["id"],
                )
                msg_w = f"งาน {row['job_title']} อยู่ระหว่างการตรวจสอบ (ชั่วโมงทำงานน้อยกว่า 90%) ทีมงานจะติดต่อกลับ"
                msg_e = f"งาน {row['job_title']} อยู่ระหว่างการตรวจสอบ (Worker ทำงานน้อยกว่า 90% ของเวลาที่กำหนด) ทีมงานจะติดต่อกลับ"
                await db.execute(
                    "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'application_update', '⚠️ งานอยู่ระหว่างตรวจสอบ', $2)",
                    row["worker_user_id"], msg_w,
                )
                await db.execute(
                    "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'application_update', '⚠️ งานอยู่ระหว่างตรวจสอบ', $2)",
                    row["employer_user_id"], msg_e,
                )
                logger.info(f"[auto_verify] disputed application {row['id']}")

            total = len(verified_rows) + len(disputed_rows)
            if total:
                logger.info(f"[auto_verify] verified={len(verified_rows)} disputed={len(disputed_rows)}")

    except Exception as e:
        logger.error(f"[auto_verify] cron error: {e}")


async def check_noshow_workers():
    """
    Cron ทุก 5 นาที: ตรวจ hired workers ที่ไม่เช็คอินหลังเวลาเริ่มงาน

    Logic:
    - งานที่มี work_start  → ใช้ work_start เป็น anchor
    - งานที่ไม่มี work_start → ใช้ start_date 08:00 Thai time เป็น anchor (fallback)
    - alert  : anchor + 10 นาที ผ่านแล้ว และยังไม่เคย alert → แจ้ง employer รอต่อหรือหา backup
    - no_show: anchor + 30 นาที ผ่านแล้ว และยังไม่ mark no_show → auto no_show + backup offer
    - จับทั้ง start_date วันนี้และก่อนหน้า (กันงานค้าง)
    - หลัง no_show → ส่ง backup offer อัตโนมัติให้ top candidate (applied/shortlisted)
    - แยก try/except ต่อ row ไม่ให้ job หนึ่ง crash หยุดทั้ง cron
    """
    if pool is None:
        return

    TH_TZ    = timezone(timedelta(hours=7))
    now_th   = datetime.now(TH_TZ)
    today_th = now_th.date()
    # now_th เป็น aware datetime → ใช้ compare กับ anchor datetime ที่สร้างใหม่

    def anchor_dt(start_date, work_start) -> datetime:
        """คืน aware datetime ของเวลาเริ่มงานจริง (Thai time)"""
        if work_start is not None:
            # work_start เป็น datetime.time object (naive) จาก asyncpg
            return datetime(
                start_date.year, start_date.month, start_date.day,
                work_start.hour, work_start.minute,
                tzinfo=TH_TZ,
            )
        # fallback: ถ้าไม่มี work_start ใช้ 08:00 Thai time
        return datetime(start_date.year, start_date.month, start_date.day, 8, 0, tzinfo=TH_TZ)

    try:
        async with pool.acquire() as db:
            # ── ดึง hired applications ที่ start_date <= วันนี้ ──────────────
            candidates = await db.fetch(
                """
                SELECT
                    ja.id,
                    ja.job_id,
                    ja.noshow_alerted_at,
                    ja.noshow_marked_at,
                    jp.title            AS job_title,
                    jp.start_date,
                    jp.work_start,
                    jp.work_end,
                    jp.daily_wage_rate,
                    jp.location,
                    wp.full_name        AS worker_name,
                    wp.user_id          AS worker_user_id,
                    ep.user_id          AS employer_user_id
                FROM   job_applications ja
                JOIN   job_postings      jp ON jp.id  = ja.job_id
                JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
                JOIN   employer_profiles ep ON ep.id  = jp.employer_id
                WHERE  ja.status           = 'hired'
                  AND  ja.noshow_marked_at IS NULL
                  AND  jp.start_date       <= $1
                """,
                today_th,
            )

            alerted_count = 0
            noshow_count  = 0

            for row in candidates:
                try:
                    anc = anchor_dt(row["start_date"], row["work_start"])
                    elapsed = now_th - anc  # timedelta

                    # ── Alert: +10 นาที → แจ้ง employer รอต่อหรือหา backup ──
                    if elapsed.total_seconds() >= 10 * 60 and row["noshow_alerted_at"] is None:
                        await db.execute(
                            "UPDATE job_applications SET noshow_alerted_at = NOW() WHERE id = $1",
                            row["id"],
                        )
                        await db.execute(
                            """
                            INSERT INTO notifications (user_id, type, title, body)
                            VALUES ($1, 'application_update', '⚠️ Worker ยังไม่เช็คอิน', $2)
                            """,
                            row["employer_user_id"],
                            f"Worker {row['worker_name']} ยังไม่เช็คอินสำหรับงาน \"{row['job_title']}\" "
                            f"(เริ่มงาน {anc.strftime('%H:%M')}) — หากไม่มาภายใน 30 นาที ระบบจะ No-Show อัตโนมัติ "
                            f"หรือไปที่ My Jobs → หา Worker สำรองได้เลย",
                        )
                        alerted_count += 1
                        logger.info(f"[noshow] alert app={row['id']} elapsed={elapsed}")

                        # ── Standby alert: แจ้ง top backup worker ให้เตรียมตัว ──
                        standby = await db.fetchrow(
                            """
                            SELECT ja2.id, wp2.user_id AS worker_user_id
                            FROM   job_applications ja2
                            JOIN   worker_profiles  wp2 ON wp2.id = ja2.worker_id
                            WHERE  ja2.job_id           = $1
                              AND  ja2.status           IN ('applied', 'shortlisted')
                              AND  ja2.backup_offered_at IS NULL
                            ORDER  BY ja2.match_score DESC
                            LIMIT  1
                            """,
                            row["job_id"],
                        )
                        if standby:
                            try:
                                await db.execute(
                                    """
                                    INSERT INTO notifications (user_id, type, title, body)
                                    VALUES ($1, 'application_update', '🟡 เตรียมตัวได้เลย', $2)
                                    """,
                                    standby["worker_user_id"],
                                    f'งาน "{row["job_title"]}" อาจมีตำแหน่งว่างให้คุณ — '
                                    f'Worker หลักยังไม่เช็คอิน หากไม่มาใน 20 นาที ระบบจะส่งงานนี้ให้คุณทันที เตรียมพร้อมไว้ได้เลย',
                                )
                                logger.info(f"[noshow] standby_notified backup_app={standby['id']} for job={row['job_id']}")
                            except Exception:
                                pass

                    # ── Auto no-show: +30 นาที ───────────────────────────────
                    if elapsed.total_seconds() >= 30 * 60:
                        async with db.transaction():
                            await db.execute(
                                "UPDATE job_applications SET status='no_show', noshow_marked_at=NOW() WHERE id=$1",
                                row["id"],
                            )
                            await db.execute(
                                "UPDATE job_postings SET slots_filled = GREATEST(0, slots_filled - 1) WHERE id=$1",
                                row["job_id"],
                            )
                            # behavioral score: noshow + 1
                            await db.execute(
                                """
                                UPDATE worker_profiles
                                SET jobs_noshow = jobs_noshow + 1
                                WHERE user_id = $1
                                """,
                                row["worker_user_id"],
                            )
                            await _recompute_reliability(db, row["worker_user_id"])
                            # แจ้ง employer
                            await db.execute(
                                """
                                INSERT INTO notifications (user_id, type, title, body)
                                VALUES ($1, 'application_update', '🚨 Worker ไม่มาทำงาน', $2)
                                """,
                                row["employer_user_id"],
                                f"Worker {row['worker_name']} ถูกทำเครื่องหมาย No-Show อัตโนมัติ "
                                f"สำหรับงาน \"{row['job_title']}\" — ระบบกำลังหา Worker สำรองให้",
                            )
                            # แจ้ง worker
                            await db.execute(
                                """
                                INSERT INTO notifications (user_id, type, title, body)
                                VALUES ($1, 'application_update', '❌ ถูกทำเครื่องหมาย No-Show', $2)
                                """,
                                row["worker_user_id"],
                                f"คุณไม่ได้เช็คอินสำหรับงาน \"{row['job_title']}\" "
                                f"ใบสมัครถูกยกเลิกอัตโนมัติ",
                            )

                            # ── คำนวณ pro-rata wage แล้วให้ employer confirm ก่อน ──
                            wage_amount  = None
                            wage_hours   = None
                            try:
                                ws = row["work_start"]
                                we = row["work_end"]
                                rate = float(row["daily_wage_rate"]) if row["daily_wage_rate"] else None
                                if ws and we and rate:
                                    total_sec = (we.hour*3600+we.minute*60) - (ws.hour*3600+ws.minute*60)
                                    if total_sec <= 0:
                                        total_sec += 86400  # ข้ามคืน
                                    # เวลาที่เหลือนับจากตอนนี้
                                    now_time_sec = now_th.hour*3600 + now_th.minute*60 + now_th.second
                                    end_sec      = we.hour*3600 + we.minute*60
                                    remaining_sec = end_sec - now_time_sec
                                    if remaining_sec < 0:
                                        remaining_sec += 86400
                                    wage_hours  = round(remaining_sec / 3600, 2)
                                    wage_amount = round(rate * remaining_sec / total_sec, 2)
                                    wage_amount = max(0.0, wage_amount)
                            except Exception as we_err:
                                logger.warning(f"[noshow] wage calc error: {we_err}")

                            # บันทึก pending wage บน job_postings
                            await db.execute(
                                """
                                UPDATE job_postings
                                SET backup_wage_pending = TRUE,
                                    backup_wage_amount  = $1,
                                    backup_wage_hours   = $2
                                WHERE id = $3
                                  AND backup_wage_confirmed_at IS NULL
                                """,
                                wage_amount, wage_hours, row["job_id"],
                            )

                            # แจ้ง employer ยืนยัน wage
                            wage_str = f"{wage_amount:,.0f}" if wage_amount else "?"
                            hours_str = f"{wage_hours:.1f}" if wage_hours else "?"
                            await db.execute(
                                """
                                INSERT INTO notifications (user_id, type, title, body)
                                VALUES ($1, 'application_update', '🚨 Worker ไม่มา — ยืนยันค่าจ้าง Worker สำรอง', $2)
                                """,
                                row["employer_user_id"],
                                f"Worker {row['worker_name']} ถูก No-Show อัตโนมัติ\n"
                                f"เวลาที่เหลือ: {hours_str} ชม. | ค่าจ้าง Worker สำรอง: {wage_str}฿\n"
                                f"กรุณายืนยันใน My Jobs ภายใน 5 นาที (ไม่กด = ยืนยันอัตโนมัติ)",
                            )
                            logger.info(f"[noshow] wage_pending job={row['job_id']} amount={wage_amount} hours={wage_hours}")

                        noshow_count += 1
                        logger.info(f"[noshow] auto no_show app={row['id']} elapsed={elapsed}")

                except Exception as row_err:
                    logger.error(f"[noshow] row error app={row['id']}: {row_err}")
                    continue

            if alerted_count or noshow_count:
                logger.info(f"[noshow] done alerted={alerted_count} no_show={noshow_count}")

            # ── Auto-start: checked_in + 30 นาที → auto working ──────────────
            auto_start_rows = await db.fetch(
                """
                SELECT
                    ja.id,
                    ja.checkin_at,
                    ja.job_id,
                    jp.title          AS job_title,
                    wp.user_id        AS worker_user_id,
                    ep.user_id        AS employer_user_id
                FROM   job_applications ja
                JOIN   job_postings      jp ON jp.id  = ja.job_id
                JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
                JOIN   employer_profiles ep ON ep.id  = jp.employer_id
                WHERE  ja.status             = 'checked_in'
                  AND  ja.auto_confirmed_at  IS NULL
                  AND  ja.checkin_at         <= NOW() - INTERVAL '30 minutes'
                """
            )
            auto_start_count = 0
            for row in auto_start_rows:
                try:
                    async with db.transaction():
                        await db.execute(
                            """
                            UPDATE job_applications
                            SET    status = 'working',
                                   work_started_at  = checkin_at,
                                   auto_confirmed_at = NOW()
                            WHERE  id = $1
                            """,
                            row["id"],
                        )
                        # แจ้ง worker
                        await db.execute(
                            """
                            INSERT INTO notifications (user_id, type, title, body)
                            VALUES ($1, 'application_update', '▶️ ระบบเริ่มนับเวลางานแล้ว', $2)
                            """,
                            row["worker_user_id"],
                            f"ระบบ Auto-Confirm งาน \"{row['job_title']}\" เพราะคุณรอ Employer เกิน 30 นาที — เวลานับตั้งแต่ที่คุณเช็คอิน",
                        )
                        # แจ้ง employer
                        await db.execute(
                            """
                            INSERT INTO notifications (user_id, type, title, body)
                            VALUES ($1, 'application_update', '⏱️ ระบบ Auto-Confirm แทนคุณแล้ว', $2)
                            """,
                            row["employer_user_id"],
                            f"ระบบเริ่มนับเวลางาน \"{row['job_title']}\" อัตโนมัติ เพราะ Worker มาถึงเกิน 30 นาทีแล้ว — เวลานับตั้งแต่ Worker เช็คอิน",
                        )
                    auto_start_count += 1
                    logger.info(f"[noshow] auto_start app={row['id']} checkin_at={row['checkin_at']}")
                except Exception as row_err:
                    logger.error(f"[noshow] auto_start error app={row['id']}: {row_err}")

            if auto_start_count:
                logger.info(f"[noshow] auto_start done count={auto_start_count}")

            # ── Auto-confirm backup wage: 5 นาที employer ไม่กด → cascade อัตโนมัติ ──
            pending_wages = await db.fetch(
                """
                SELECT jp.id          AS job_id,
                       jp.backup_wage_amount,
                       jp.backup_wage_hours,
                       jp.title       AS job_title
                FROM   job_postings jp
                WHERE  jp.backup_wage_pending        = TRUE
                  AND  jp.backup_wage_confirmed_at  IS NULL
                  AND  EXISTS (
                      SELECT 1 FROM job_applications
                      WHERE  job_id           = jp.id
                        AND  status           = 'no_show'
                        AND  noshow_marked_at <= NOW() - INTERVAL '5 minutes'
                  )
                """
            )
            for pw in pending_wages:
                try:
                    await _cascade_backup_offer(
                        db, pw["job_id"],
                        pw["backup_wage_amount"], pw["backup_wage_hours"],
                        pw["job_title"], auto_confirmed=True,
                    )
                    logger.info(f"[noshow] auto_wage_confirmed job={pw['job_id']}")
                except Exception as pw_err:
                    logger.error(f"[noshow] auto_wage_confirm error job={pw['job_id']}: {pw_err}")

    except Exception as e:
        logger.error(f"[noshow] cron error: {e}")


async def send_d1_reminders():
    """Cron ทุกวัน 18:00 Thai time (11:00 UTC): แจ้งเตือน D-1 ก่อนวันทำงาน"""
    if pool is None:
        return
    TH_TZ       = timezone(timedelta(hours=7))
    tomorrow_th = (datetime.now(TH_TZ) + timedelta(days=1)).date()

    try:
        async with pool.acquire() as db:
            rows = await db.fetch(
                """
                SELECT
                    ja.id,
                    jp.title          AS job_title,
                    jp.work_start,
                    jp.location_name,
                    ep.company_name,
                    wp.user_id        AS worker_user_id
                FROM   job_applications ja
                JOIN   job_postings      jp ON jp.id  = ja.job_id
                JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
                JOIN   employer_profiles ep ON ep.id  = jp.employer_id
                WHERE  ja.status    = 'hired'
                  AND  jp.start_date = $1
                """,
                tomorrow_th,
            )
            for row in rows:
                work_time = str(row["work_start"])[:5] if row["work_start"] else "ไม่ระบุ"
                location  = row["location_name"] or "สถานที่ทำงาน"
                await db.execute(
                    """
                    INSERT INTO notifications (user_id, type, title, body)
                    VALUES ($1, 'application_update', '🔔 แจ้งเตือนงานพรุ่งนี้', $2)
                    """,
                    row["worker_user_id"],
                    f"พรุ่งนี้คุณมีงาน \"{row['job_title']}\" กับ {row['company_name']} "
                    f"เริ่ม {work_time} น. ที่ {location} — กรุณาเตรียมตัวและเช็คอินให้ตรงเวลา",
                )
                logger.info(f"[d1reminder] reminder sent for application {row['id']}")

            if rows:
                logger.info(f"[d1reminder] sent {len(rows)} reminders for {tomorrow_th}")

    except Exception as e:
        logger.error(f"[d1reminder] cron error: {e}")


async def check_expired_jobs():
    """Cron ทุก 30 นาที: ปิด job ที่ถึง auto_close_at แล้ว และยังไม่มี hired worker"""
    if pool is None:
        return
    try:
        async with pool.acquire() as db:
            jobs = await db.fetch(
                """
                SELECT jp.id, jp.title, ep.user_id AS employer_user_id
                FROM   job_postings      jp
                JOIN   employer_profiles ep ON ep.id = jp.employer_id
                WHERE  jp.status = 'open'
                  AND  jp.auto_close_at <= NOW()
                  AND  jp.slots_filled = 0
                  AND  NOT EXISTS (
                      SELECT 1 FROM job_applications
                      WHERE  job_id = jp.id
                        AND  status IN ('hired','checked_in','working','completed','verified')
                  )
                """
            )
            closed_count = 0
            for job in jobs:
                total_apps = await db.fetchval(
                    "SELECT COUNT(*) FROM job_applications WHERE job_id=$1", job["id"]
                )
                if total_apps == 0:
                    reason = "no_applicants"
                    msg = (f"งาน '{job['title']}' ของคุณปิดอัตโนมัติ "
                           f"เนื่องจากไม่มีผู้สมัครภายใน 48 ชม. ก่อนวันเริ่มงาน ")
                else:
                    reason = "no_hire"
                    msg = (f"งาน '{job['title']}' ของคุณปิดอัตโนมัติ "
                           f"เนื่องจากยังไม่ได้เลือกผู้สมัครภายใน 48 ชม. ก่อนวันเริ่มงาน ")

                await db.execute(
                    "UPDATE job_postings SET status='closed', auto_closed_reason=$1 WHERE id=$2",
                    reason, job["id"],
                )
                await db.execute(
                    "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'job_auto_closed', '⏰ งานปิดอัตโนมัติ', $2)",
                    job["employer_user_id"], msg,
                )
                logger.info(
                    f"[check_expired_jobs] closed job={job['id']} reason={reason} "
                    f"apps={total_apps}"
                )
                closed_count += 1

            logger.info(f"[check_expired_jobs] done closed={closed_count}")
    except Exception as e:
        logger.error(f"[check_expired_jobs] cron error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
        statement_cache_size=0,  # Required for Supabase PgBouncer transaction mode
    )
    print("✅ DB pool connected")
    print(f"[startup] FRONTEND_URL = {settings.frontend_url!r}")
    logger.info(f"[startup] FRONTEND_URL   = {settings.frontend_url!r}")
    logger.info(f"[startup] CORS_ORIGINS   = {settings.cors_origins!r}")
    logger.info(f"[startup] origins list   = {origins}")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_verify_completed_jobs, "interval", minutes=30)
    scheduler.add_job(check_noshow_workers,       "interval", minutes=5)
    scheduler.add_job(send_d1_reminders,          "cron",     hour=11, minute=0)   # 11:00 UTC = 18:00 Bangkok
    scheduler.add_job(check_expired_jobs,         "interval", minutes=30)
    scheduler.start()
    print("⏰ Schedulers started: auto-verify(30m) | noshow-check(5m) | D-1 reminder(18:00 BKK) | job-expiry(30m)")

    yield

    scheduler.shutdown(wait=False)
    await pool.close()
    print("🔌 DB pool closed")

async def get_db() -> asyncpg.Connection:
    async with pool.acquire() as conn:
        yield conn


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="WeHire API",
    version="0.1.0",
    description="Daily Wage Matchmaking Platform — BKK MVP",
    lifespan=lifespan,
    docs_url=None if os.getenv("RAILWAY_ENVIRONMENT") else "/docs",
    redoc_url=None if os.getenv("RAILWAY_ENVIRONMENT") else "/redoc",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "คำขอมากเกินไป กรุณารอสักครู่แล้วลองใหม่"})
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if settings.frontend_url:
    origins.append(settings.frontend_url.strip())
# Explicit allowlist — current Cloudflare Worker URL
for _url in [
    "https://wearehiredmvp.vi-nutthaphat.workers.dev",
]:
    if _url not in origins:
        origins.append(_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# JWT Helpers
# ---------------------------------------------------------------------------

security = HTTPBearer()

def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub":  user_id,
        "role": role,
        "exp":  datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
        "iat":  datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token หมดอายุ กรุณาเข้าสู่ระบบใหม่")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token ไม่ถูกต้อง")

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    payload = decode_token(creds.credentials)
    if pool:
        async with pool.acquire() as db:
            is_active = await db.fetchval(
                "SELECT is_active FROM users WHERE id=$1", UUID(payload["sub"])
            )
            if is_active is False:
                raise HTTPException(status_code=403, detail="บัญชีถูกระงับ")
    return payload

async def require_worker(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "worker":
        raise HTTPException(status_code=403, detail="เฉพาะ Worker เท่านั้น")
    return user

async def require_employer(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "employer":
        raise HTTPException(status_code=403, detail="เฉพาะ Employer เท่านั้น")
    return user

async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="เฉพาะ Admin เท่านั้น")
    return user


# ---------------------------------------------------------------------------
# Supabase Storage Helpers
# ---------------------------------------------------------------------------
_KYC_BUCKET = "kyc-documents"
_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def _storage_upload(path: str, data: bytes, content_type: str) -> None:
    """Upload bytes to Supabase Storage (upsert)."""
    if not settings.supabase_service_key:
        raise HTTPException(status_code=500, detail="SUPABASE_SERVICE_KEY ยังไม่ได้ตั้งค่า")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{settings.supabase_url}/storage/v1/object/{_KYC_BUCKET}/{path}",
            headers={
                "Authorization": f"Bearer {settings.supabase_service_key}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            content=data,
        )
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f"Storage upload ล้มเหลว: {r.text[:200]}")


async def _storage_signed_url(path: str) -> str:
    """Get 1-hour signed URL for a KYC storage path. Returns '' on failure."""
    if not settings.supabase_service_key or not path:
        return ""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{settings.supabase_url}/storage/v1/object/sign/{_KYC_BUCKET}/{path}",
            headers={"Authorization": f"Bearer {settings.supabase_service_key}"},
            json={"expiresIn": 3600},
        )
        if r.status_code != 200:
            return ""
        signed = r.json().get("signedURL", "")
        if not signed:
            return ""
        if signed.startswith("http"):
            return signed
        return f"{settings.supabase_url}/storage/v1{signed}"


# ============================================================
# AUTH ROUTES
# ============================================================

# ── Google OAuth via Supabase ──────────────────────────────

class GoogleCallbackRequest(BaseModel):
    access_token: str          # Supabase session access_token
    role:         str = Field(..., pattern="^(worker|employer)$")

@app.get("/auth/google/url", tags=["Auth"])
async def google_login_url(role: str = "worker"):
    """Frontend เรียกเพื่อได้ redirect URL ไป Google"""
    if role not in ("worker", "employer"):
        raise HTTPException(status_code=400, detail="role ไม่ถูกต้อง")
    url = (
        f"{settings.supabase_url}/auth/v1/authorize"
        f"?provider=google"
        f"&redirect_to={settings.frontend_url}/index.html%3Frole%3D{role}"
    )
    return {"url": url}

@app.post("/auth/google/callback", tags=["Auth"])
async def google_callback(
    body: GoogleCallbackRequest,
    db:   asyncpg.Connection = Depends(get_db),
):
    """
    Frontend ได้ Supabase session access_token แล้วส่งมาที่นี่
    Backend verify ด้วย Supabase JWKS (ES256) → สร้าง/หา user ใน DB → ออก JWT ของเรา
    """
    from jwt.algorithms import ECAlgorithm
    try:
        # ดึง JWKS จาก Supabase
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json")
            r.raise_for_status()
            jwks = r.json()

        # หา public key ที่ตรงกับ kid ใน token header
        header = jwt.get_unverified_header(body.access_token)
        kid = header.get("kid")
        public_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                public_key = ECAlgorithm.from_jwk(key)
                break

        if not public_key:
            raise HTTPException(status_code=401, detail="ไม่พบ signing key สำหรับ token นี้")

        payload = jwt.decode(
            body.access_token,
            public_key,
            algorithms=["ES256"],
            options={"verify_aud": False},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[google_callback] verify failed | token[:60]={body.access_token[:60]!r} | error={type(e).__name__}: {e}")
        raise HTTPException(status_code=401, detail=f"Token ไม่ถูกต้อง: {e}")

    supabase_uid = payload.get("sub")
    email        = payload.get("email") or payload.get("user_metadata", {}).get("email", "")

    if not email:
        raise HTTPException(status_code=400, detail="ไม่พบ email จาก Google")

    # Upsert user ใน DB ของเรา
    user = await db.fetchrow(
        """
        INSERT INTO users (email, password_hash, role)
        VALUES ($1, 'google_oauth', $2)
        ON CONFLICT (email) DO UPDATE
            SET role = CASE
                WHEN users.password_hash = 'google_oauth' THEN $2
                ELSE users.role   -- ถ้า email มีอยู่แล้ว (สมัครด้วย password) ไม่เปลี่ยน role
            END
        RETURNING id, role, is_active
        """,
        email, body.role,
    )

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="บัญชีถูกระงับ")

    token = create_token(str(user["id"]), user["role"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user["role"],
        "user_id":      str(user["id"]),
    }


class RegisterRequest(BaseModel):
    email:    EmailStr
    password: str  = Field(..., min_length=6, max_length=100)
    role:     str  = Field(..., pattern="^(worker|employer)$")
    phone:    Optional[str] = Field(None, max_length=20)

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

@app.post("/auth/register", status_code=201, tags=["Auth"])
async def register(body: RegisterRequest, db: asyncpg.Connection = Depends(get_db)):
    # Check duplicate
    existing = await db.fetchval("SELECT id FROM users WHERE email=$1", body.email)
    if existing:
        raise HTTPException(status_code=409, detail="อีเมลนี้ถูกใช้งานแล้ว")

    if body.phone:
        existing_phone = await db.fetchval("SELECT id FROM users WHERE phone=$1", body.phone)
        if existing_phone:
            raise HTTPException(status_code=409, detail="เบอร์โทรนี้ถูกใช้งานแล้ว")

    # Hash password (bcrypt cost=12 — ปลอดภัยดี ไม่แรงเกิน)
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt(rounds=12)).decode()

    user = await db.fetchrow(
        """
        INSERT INTO users (email, phone, password_hash, role)
        VALUES ($1, $2, $3, $4)
        RETURNING id, role
        """,
        body.email, body.phone, hashed, body.role,
    )

    token = create_token(str(user["id"]), user["role"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user["role"],
        "user_id":      str(user["id"]),
    }


@app.post("/auth/login", tags=["Auth"])
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: asyncpg.Connection = Depends(get_db)):
    user = await db.fetchrow(
        "SELECT id, password_hash, role, is_active FROM users WHERE email=$1",
        body.email,
    )
    if not user:
        raise HTTPException(status_code=401, detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="บัญชีถูกระงับ")

    if not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง")

    token = create_token(str(user["id"]), user["role"])
    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user["role"],
        "user_id":      str(user["id"]),
    }


@app.get("/auth/me", tags=["Auth"])
async def me(user: dict = Depends(get_current_user), db: asyncpg.Connection = Depends(get_db)):
    row = await db.fetchrow(
        "SELECT id, email, phone, role, created_at FROM users WHERE id=$1",
        UUID(user["sub"]),
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
    return dict(row)


# ============================================================
# WORKER PROFILE
# ============================================================

class WorkerProfileCreate(BaseModel):
    full_name:           str   = Field(..., min_length=1, max_length=100)
    skills:              list[str] = Field(default=[])
    experience_years:    int   = Field(default=0, ge=0, le=50)
    daily_rate_expected: Optional[float] = Field(None, gt=0)
    lat:                 float = Field(..., ge=-90,  le=90)
    lng:                 float = Field(..., ge=-180, le=180)
    location_name:       Optional[str] = Field(None, max_length=255)

class WorkerProfileUpdate(BaseModel):
    skills:              Optional[list[str]] = None
    experience_years:    Optional[int]       = Field(None, ge=0, le=50)
    daily_rate_expected: Optional[float]     = Field(None, gt=0)
    lat:                 Optional[float]     = Field(None, ge=-90,  le=90)
    lng:                 Optional[float]     = Field(None, ge=-180, le=180)
    location_name:       Optional[str]       = Field(None, max_length=255)
    is_available:        Optional[bool]      = None
    nationality_type:    Optional[str]       = Field(None, pattern="^(thai|foreign)$")

@app.get("/workers/profile/me", tags=["Worker"])
async def get_worker_profile(
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT id, full_name, skills, experience_years, daily_rate_expected,
               background_check_status, location_name, is_available,
               nationality_type, work_permit_url, work_permit_expiry,
               ST_X(location::geometry) AS lng,
               ST_Y(location::geometry) AS lat,
               updated_at
        FROM   worker_profiles
        WHERE  user_id = $1
        """,
        UUID(user["sub"]),
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Worker")
    return dict(row)

@app.post("/workers/kyc/upload", tags=["Worker"])
async def upload_kyc_photos(
    face_photo:    UploadFile = File(...),
    id_card_photo: UploadFile = File(...),
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    """Worker ส่งรูปถ่ายหน้าตรง + บัตรประชาชน เพื่อยืนยัน KYC"""
    face_data    = await face_photo.read()
    id_card_data = await id_card_photo.read()

    for data, f, label in [
        (face_data, face_photo, "รูปถ่ายหน้าตรง"),
        (id_card_data, id_card_photo, "บัตรประชาชน"),
    ]:
        if f.content_type not in _ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail=f"{label}: รองรับเฉพาะ JPG, PNG, WebP")
        if len(data) > _MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"{label}: ขนาดไฟล์ต้องไม่เกิน 5MB")

    worker_id = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not worker_id:
        raise HTTPException(status_code=404, detail="ไม่พบ Worker Profile")

    face_path    = f"kyc/{worker_id}/face.jpg"
    id_card_path = f"kyc/{worker_id}/id_card.jpg"

    await _storage_upload(face_path,    face_data,    face_photo.content_type)
    await _storage_upload(id_card_path, id_card_data, id_card_photo.content_type)

    await db.execute(
        """
        UPDATE worker_profiles
        SET    face_photo_url          = $1,
               id_card_photo_url       = $2,
               kyc_submitted_at        = NOW(),
               background_check_status = 'pending'
        WHERE  id = $3
        """,
        face_path, id_card_path, worker_id,
    )
    return {"success": True, "message": "ส่งเอกสาร KYC สำเร็จ รอ Admin ตรวจสอบ"}


@app.post("/workers/profile", status_code=201, tags=["Worker"])
async def create_worker_profile(
    body: WorkerProfileCreate,
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    existing = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if existing:
        raise HTTPException(status_code=409, detail="มีโปรไฟล์อยู่แล้ว ใช้ PATCH แทน")

    # Clean skills — lowercase + dedupe
    clean_skills = list({s.strip().lower() for s in body.skills if s.strip()})

    row = await db.fetchrow(
        """
        INSERT INTO worker_profiles
            (user_id, full_name, skills, experience_years, daily_rate_expected,
             location, location_name)
        VALUES
            ($1, $2, $3, $4, $5,
             ST_MakePoint($6, $7)::geography, $8)
        RETURNING id, full_name, skills, experience_years, daily_rate_expected,
                  background_check_status, location_name, is_available
        """,
        UUID(user["sub"]), body.full_name, clean_skills,
        body.experience_years, body.daily_rate_expected,
        body.lng, body.lat, body.location_name,
    )
    return dict(row)

@app.patch("/workers/profile", tags=["Worker"])
async def update_worker_profile(
    body: WorkerProfileUpdate,
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    # Build dynamic SET clause — only update fields provided
    updates = {}
    if body.skills is not None:
        updates["skills"] = list({s.strip().lower() for s in body.skills if s.strip()})
    if body.experience_years is not None:
        updates["experience_years"] = body.experience_years
    if body.daily_rate_expected is not None:
        updates["daily_rate_expected"] = body.daily_rate_expected
    if body.location_name is not None:
        updates["location_name"] = body.location_name
    if body.is_available is not None:
        updates["is_available"] = body.is_available
    if body.nationality_type is not None:
        updates["nationality_type"] = body.nationality_type

    if not updates and body.lat is None:
        raise HTTPException(status_code=400, detail="ไม่มีข้อมูลที่ต้องอัปเดต")

    # Build parameterized query
    set_parts = []
    params    = []
    idx       = 1

    for key, val in updates.items():
        set_parts.append(f"{key} = ${idx}")
        params.append(val)
        idx += 1

    if body.lat is not None and body.lng is not None:
        set_parts.append(f"location = ST_MakePoint(${idx}, ${idx+1})::geography")
        params.extend([body.lng, body.lat])
        idx += 2

    params.append(UUID(user["sub"]))
    query = f"""
        UPDATE worker_profiles
        SET    {', '.join(set_parts)}
        WHERE  user_id = ${idx}
        RETURNING id, full_name, skills, experience_years, daily_rate_expected,
                  background_check_status, location_name, is_available
    """
    row = await db.fetchrow(query, *params)
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Worker")
    return dict(row)


# ============================================================
# EMPLOYER PROFILE
# ============================================================

class EmployerProfileCreate(BaseModel):
    company_name:   str = Field(..., min_length=1, max_length=200)
    business_type:  Optional[str] = Field(None, max_length=100)
    contact_person: str = Field(..., min_length=1, max_length=100)

class EmployerProfileUpdate(BaseModel):
    company_name:   Optional[str] = Field(None, min_length=1, max_length=200)
    business_type:  Optional[str] = Field(None, max_length=100)
    contact_person: Optional[str] = Field(None, min_length=1, max_length=100)

@app.get("/employers/profile/me", tags=["Employer"])
async def get_employer_profile(
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT id, user_id, company_name, business_type, contact_person, verified_status, created_at
        FROM   employer_profiles
        WHERE  user_id = $1
        """,
        UUID(user["sub"]),
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Employer")
    return dict(row)

@app.post("/employers/profile", status_code=201, tags=["Employer"])
async def create_employer_profile(
    body: EmployerProfileCreate,
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    existing = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if existing:
        raise HTTPException(status_code=409, detail="มีโปรไฟล์อยู่แล้ว ใช้ PATCH แทน")

    row = await db.fetchrow(
        """
        INSERT INTO employer_profiles (user_id, company_name, business_type, contact_person)
        VALUES ($1, $2, $3, $4)
        RETURNING id, company_name, business_type, contact_person, verified_status
        """,
        UUID(user["sub"]), body.company_name, body.business_type, body.contact_person,
    )
    return dict(row)

@app.patch("/employers/profile", tags=["Employer"])
async def update_employer_profile(
    body: EmployerProfileUpdate,
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="ไม่มีข้อมูลที่ต้องอัปเดต")

    set_parts = []
    params    = []
    for idx, (key, val) in enumerate(updates.items(), start=1):
        set_parts.append(f"{key} = ${idx}")
        params.append(val)
    params.append(UUID(user["sub"]))

    query = f"""
        UPDATE employer_profiles
        SET    {', '.join(set_parts)}
        WHERE  user_id = ${len(params)}
        RETURNING id, company_name, business_type, contact_person, verified_status
    """
    row = await db.fetchrow(query, *params)
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบโปรไฟล์ Employer")
    return dict(row)


# ============================================================
# JOB POSTINGS
# ============================================================

class JobCreate(BaseModel):
    title:           str   = Field(..., min_length=1, max_length=200)
    description:     Optional[str] = None
    required_skills: list[str]     = Field(default=[])
    daily_wage_rate: float          = Field(..., gt=0)
    duration_days:   int            = Field(..., gt=0)
    slots_available: int            = Field(default=1, gt=0, le=500)
    lat:             float          = Field(..., ge=-90,  le=90)
    lng:             float          = Field(..., ge=-180, le=180)
    location_name:   Optional[str] = Field(None, max_length=255)
    zone_name:       Optional[str] = Field(None, max_length=30)
    start_date:      Optional[str] = None   # ISO date string
    work_start:      Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")  # "08:00"
    work_end:        Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")  # "17:00"
    ot_rate:         Optional[float] = Field(None, ge=0)  # ฿/ชม. OT

class JobStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(open|closed|draft)$")

class AdminUserStatus(BaseModel):
    status: str = Field(..., pattern="^(active|suspended|banned)$")

class AdminKYCReview(BaseModel):
    decision: str = Field(..., pattern="^(verified|failed)$")
    note: Optional[str] = None

class AdminDisputeResolve(BaseModel):
    decision: str = Field(..., pattern="^(worker_win|employer_win)$")
    note: Optional[str] = None

class AdminJobStatus(BaseModel):
    status: str = Field(..., pattern="^(open|closed|expired)$")

@app.post("/jobs", status_code=201, tags=["Jobs"])
async def post_job(
    body: JobCreate,
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    # Get employer profile id
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not emp_id:
        raise HTTPException(status_code=404, detail="สร้าง Employer Profile ก่อน")

    clean_skills = list({s.strip().lower() for s in body.required_skills if s.strip()})

    start_date = None
    if body.start_date:
        from datetime import date
        try:
            start_date = date.fromisoformat(body.start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="start_date format ไม่ถูกต้อง (YYYY-MM-DD)")

    # คำนวณ auto_close_at
    if start_date:
        auto_close_at = datetime(start_date.year, start_date.month, start_date.day,
                                 tzinfo=timezone.utc) - timedelta(hours=48)
    else:
        auto_close_at = datetime.now(timezone.utc) + timedelta(days=7)

    # แปลง string "HH:MM" → datetime.time ก่อนส่ง asyncpg (asyncpg ไม่รับ string สำหรับ TIME column)
    from datetime import time as time_type
    work_start_t = time_type.fromisoformat(body.work_start) if body.work_start else None
    work_end_t   = time_type.fromisoformat(body.work_end)   if body.work_end   else None

    # Validate work hours ≤ 8
    if work_start_t and work_end_t:
        start_min = work_start_t.hour * 60 + work_start_t.minute
        end_min   = work_end_t.hour   * 60 + work_end_t.minute
        if end_min <= start_min:
            end_min += 24 * 60  # ข้ามคืน
        if (end_min - start_min) > 8 * 60:
            raise HTTPException(status_code=400, detail="ช่วงเวลาทำงานต้องไม่เกิน 8 ชั่วโมง")

    row = await db.fetchrow(
        """
        INSERT INTO job_postings
            (employer_id, title, description, required_skills, daily_wage_rate,
             duration_days, slots_available, location, location_name, zone_name,
             start_date, work_start, work_end, ot_rate, auto_close_at)
        VALUES
            ($1, $2, $3, $4, $5, $6, $7,
             ST_MakePoint($8, $9)::geography, $10, $11, $12, $13, $14, $15, $16)
        RETURNING id, title, status, created_at, auto_close_at
        """,
        emp_id, body.title, body.description, clean_skills,
        body.daily_wage_rate, body.duration_days, body.slots_available,
        body.lng, body.lat, body.location_name, body.zone_name, start_date,
        work_start_t, work_end_t, body.ot_rate, auto_close_at,
    )
    return dict(row)

@app.get("/employers/last-location", tags=["Employer"])
async def get_last_job_location(
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    """Return location from employer's most recent job posting."""
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not emp_id:
        return {}
    row = await db.fetchrow(
        """
        SELECT location_name,
               ST_Y(location::geometry) AS lat,
               ST_X(location::geometry) AS lng
        FROM   job_postings
        WHERE  employer_id = $1
          AND  location IS NOT NULL
        ORDER  BY created_at DESC
        LIMIT  1
        """,
        emp_id,
    )
    if not row:
        return {}
    return {
        "location_name": row["location_name"],
        "lat":           float(row["lat"]),
        "lng":           float(row["lng"]),
    }

@app.get("/jobs/mine", tags=["Jobs"])
async def get_my_jobs(
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not emp_id:
        return []

    rows = await db.fetch(
        """
        SELECT id, title, status, daily_wage_rate, duration_days,
               slots_available, slots_filled, location_name, zone_name,
               start_date, created_at, auto_close_at, auto_closed_reason,
               backup_wage_pending, backup_wage_amount, backup_wage_hours
        FROM   job_postings
        WHERE  employer_id = $1
        ORDER  BY created_at DESC
        LIMIT  100
        """,
        emp_id,
    )
    result = []
    for r in rows:
        d = dict(r)
        d["daily_wage_rate"]    = float(d["daily_wage_rate"]) if d["daily_wage_rate"] else None
        d["backup_wage_amount"] = float(d["backup_wage_amount"]) if d["backup_wage_amount"] else None
        d["backup_wage_hours"]  = float(d["backup_wage_hours"]) if d["backup_wage_hours"] else None
        result.append(d)
    return result

@app.patch("/jobs/{job_id}/status", tags=["Jobs"])
async def update_job_status(
    job_id: UUID,
    body:   JobStatusUpdate,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        "SELECT id FROM job_postings WHERE id=$1 AND employer_id=$2",
        job_id, emp_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบงาน หรือไม่มีสิทธิ์แก้ไข")
    await db.execute(
        "UPDATE job_postings SET status=$1 WHERE id=$2", body.status, job_id
    )
    return {"job_id": job_id, "status": body.status}


# ============================================================
# WORKER EARNINGS
# ============================================================

@app.get("/workers/earnings", tags=["Worker"])
async def get_my_earnings(
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    """รายได้ทั้งหมดของ worker จากงานที่ verified แล้ว"""
    worker_id = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not worker_id:
        return {"total": 0, "transactions": []}

    rows = await db.fetch(
        """
        SELECT
            ja.id,
            ja.work_started_at,
            ja.work_ended_at,
            ja.employer_verified_at,
            ja.backup_confirmed_wage,
            jp.title          AS job_title,
            jp.daily_wage_rate,
            jp.work_start,
            jp.work_end,
            jp.start_date,
            ep.company_name
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  ja.worker_id = $1
          AND  ja.status    = 'verified'
        ORDER  BY ja.employer_verified_at DESC
        """,
        worker_id,
    )

    transactions = []
    total = 0.0

    for r in rows:
        # ถ้าเป็น backup worker ใช้ backup_confirmed_wage
        if r["backup_confirmed_wage"]:
            amount = float(r["backup_confirmed_wage"])
        else:
            # คำนวณจาก actual hours worked
            if r["work_started_at"] and r["work_ended_at"]:
                actual_sec = (r["work_ended_at"] - r["work_started_at"]).total_seconds()
                # เทียบกับ expected hours
                ws = r["work_start"]
                we = r["work_end"]
                if ws and we:
                    total_sec = (we.hour*3600+we.minute*60) - (ws.hour*3600+ws.minute*60)
                    if total_sec <= 0:
                        total_sec += 86400
                    ratio = min(actual_sec / total_sec, 1.0)
                    amount = round(float(r["daily_wage_rate"]) * ratio, 2)
                else:
                    amount = float(r["daily_wage_rate"])
            else:
                amount = float(r["daily_wage_rate"])

        total += amount
        transactions.append({
            "id":           str(r["id"]),
            "job_title":    r["job_title"],
            "company_name": r["company_name"],
            "date":         r["start_date"].isoformat() if r["start_date"] else None,
            "verified_at":  r["employer_verified_at"].isoformat() if r["employer_verified_at"] else None,
            "amount":       amount,
            "is_backup":    r["backup_confirmed_wage"] is not None,
            "is_estimate":  r["backup_confirmed_wage"] is None and r["work_ended_at"] is None,
        })

    return {
        "total":        round(total, 2),
        "count":        len(transactions),
        "transactions": transactions,
    }


# ============================================================
# WORKER APPLICATIONS
# ============================================================


@app.get("/workers/applications", tags=["Worker"])
async def get_my_applications(
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    worker_id = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if not worker_id:
        return []

    rows = await db.fetch(
        """
        SELECT
            ja.id, ja.status, ja.match_score, ja.distance_km,
            ja.matched_skills, ja.employer_note, ja.applied_at,
            ja.checkin_at, ja.work_started_at, ja.work_ended_at, ja.employer_verified_at,
            ja.auto_confirm_start,
            ja.backup_offered_at,
            ja.backup_accepted_at,
            ja.backup_confirmed_wage,
            jp.id          AS job_id,
            jp.title       AS job_title,
            jp.daily_wage_rate,
            jp.duration_days,
            jp.location_name,
            jp.work_start, jp.work_end, jp.ot_rate,
            ST_Y(jp.location::geometry) AS job_lat,
            ST_X(jp.location::geometry) AS job_lng
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.worker_id = $1
        ORDER  BY ja.applied_at DESC
        """,
        worker_id,
    )
    MAPS_STATUSES = {"hired", "checked_in", "working", "completed", "verified"}
    return [
        {
            "id":                    str(r["id"]),
            "status":                r["status"],
            "match_score":           float(r["match_score"] or 0),
            "distance_km":           float(r["distance_km"] or 0),
            "matched_skills":        r["matched_skills"] or [],
            "employer_note":         r["employer_note"],
            "applied_at":            r["applied_at"].isoformat(),
            "checkin_at":            r["checkin_at"].isoformat() if r["checkin_at"] else None,
            "work_started_at":       r["work_started_at"].isoformat() if r["work_started_at"] else None,
            "work_ended_at":         r["work_ended_at"].isoformat() if r["work_ended_at"] else None,
            "employer_verified_at":  r["employer_verified_at"].isoformat() if r["employer_verified_at"] else None,
            "auto_confirm_start":    r["auto_confirm_start"],
            "backup_offered_at":     r["backup_offered_at"].isoformat() if r["backup_offered_at"] else None,
            "backup_accepted_at":    r["backup_accepted_at"].isoformat() if r["backup_accepted_at"] else None,
            "backup_confirmed_wage": float(r["backup_confirmed_wage"]) if r["backup_confirmed_wage"] else None,
            "maps_link":             (
                f"https://www.google.com/maps/dir/?api=1&destination={r['job_lat']},{r['job_lng']}"
                if r["status"] in MAPS_STATUSES else None
            ),
            "job": {
                "id":              str(r["job_id"]),
                "title":           r["job_title"],
                "daily_wage_rate": float(r["daily_wage_rate"]),
                "duration_days":   r["duration_days"],
                "location_name":   r["location_name"],
                "work_start":      str(r["work_start"])[:5] if r["work_start"] else None,
                "work_end":        str(r["work_end"])[:5]   if r["work_end"]   else None,
                "ot_rate":         float(r["ot_rate"]) if r["ot_rate"] else None,
            }
        }
        for r in rows
    ]


# ============================================================
# MATCHING ENGINE (from matching_engine.py — wired with real auth)
# ============================================================

DEFAULT_RADIUS_KM = 10.0
MAX_RADIUS_KM     = 30.0
W_SKILLS   = 0.60
W_DISTANCE = 0.25
W_RATE     = 0.15

def compute_match_score(
    worker_skills:   list[str],
    required_skills: list[str],
    distance_km:     float,
    radius_km:       float,
    worker_rate:     Optional[float],
    job_rate:        float,
) -> tuple[float, list[str], list[str]]:
    required_set = set(s.lower() for s in required_skills)
    worker_set   = set(s.lower() for s in worker_skills)
    matched      = list(worker_set & required_set)
    missing      = list(required_set - worker_set)

    skill_score    = len(matched) / len(required_set) if required_set else 1.0
    distance_score = max(0.0, 1.0 - (distance_km / radius_km))

    if worker_rate and job_rate > 0:
        ratio = float(worker_rate) / float(job_rate)
        rate_score = 1.0 if ratio <= 1.0 else (1.0 - (ratio - 1.0) / 0.2 if ratio <= 1.2 else 0.0)
    else:
        rate_score = 0.5

    raw   = W_SKILLS * skill_score + W_DISTANCE * distance_score + W_RATE * rate_score
    score = round(raw * 100, 2)
    return score, [s.title() for s in matched], [s.title() for s in missing]


class ApplyRequest(BaseModel):
    lat: float = Field(..., ge=-90,  le=90)
    lng: float = Field(..., ge=-180, le=180)

@app.post("/jobs/{job_id}/apply", status_code=201, tags=["Matching"])
@limiter.limit("20/minute")
async def apply_to_job(
    request: Request,
    job_id: UUID,
    body:   ApplyRequest,
    user:   dict = Depends(require_worker),
    db:     asyncpg.Connection = Depends(get_db),
):
    job = await db.fetchrow(
        """
        SELECT id, required_skills, daily_wage_rate, slots_available, slots_filled, status
        FROM   job_postings
        WHERE  id = $1
        """,
        job_id,
    )
    if not job:
        raise HTTPException(status_code=404, detail="ไม่พบงาน")
    if job["status"] != "open":
        raise HTTPException(status_code=409, detail="งานนี้ปิดรับสมัครแล้ว")
    if job["slots_filled"] >= job["slots_available"]:
        raise HTTPException(status_code=409, detail="ที่นั่งเต็มแล้ว")

    worker = await db.fetchrow(
        """SELECT id, skills, daily_rate_expected,
                  nationality_type, work_permit_url, work_permit_expiry
           FROM   worker_profiles WHERE user_id=$1""",
        UUID(user["sub"]),
    )
    if not worker:
        raise HTTPException(status_code=404, detail="สร้าง Worker Profile ก่อน")

    # Work Permit enforcement — แรงงานต่างด้าวต้องมี Work Permit ที่ยังไม่หมดอายุ
    if worker["nationality_type"] == "foreign":
        from datetime import date as date_type
        if not worker["work_permit_url"]:
            raise HTTPException(
                status_code=403,
                detail="กรุณา upload Work Permit ก่อนสมัครงาน",
            )
        if not worker["work_permit_expiry"] or worker["work_permit_expiry"] < date_type.today():
            raise HTTPException(
                status_code=403,
                detail="Work Permit หมดอายุแล้ว กรุณาอัปเดตเอกสารก่อนสมัครงาน",
            )

    dist_row = await db.fetchrow(
        """
        SELECT ST_Distance(
            ST_MakePoint($1, $2)::geography,
            location
        ) / 1000.0 AS distance_km
        FROM job_postings WHERE id = $3
        """,
        body.lng, body.lat, job_id,
    )
    distance_km = float(dist_row["distance_km"])

    if distance_km > MAX_RADIUS_KM:
        raise HTTPException(
            status_code=400,
            detail=f"งานอยู่ห่าง {distance_km:.1f} กม. เกินรัศมี {MAX_RADIUS_KM} กม.",
        )

    score, matched_skills, missing_skills = compute_match_score(
        worker_skills   = worker["skills"] or [],
        required_skills = job["required_skills"] or [],
        distance_km     = distance_km,
        radius_km       = DEFAULT_RADIUS_KM,
        worker_rate     = worker["daily_rate_expected"],
        job_rate        = float(job["daily_wage_rate"]),
    )

    app_row = await db.fetchrow(
        """
        INSERT INTO job_applications
            (job_id, worker_id, status, match_score, distance_km, matched_skills)
        VALUES ($1, $2, 'applied', $3, $4, $5)
        ON CONFLICT (job_id, worker_id)
            DO UPDATE SET
                status         = 'applied',
                match_score    = EXCLUDED.match_score,
                distance_km    = EXCLUDED.distance_km,
                matched_skills = EXCLUDED.matched_skills,
                applied_at     = NOW()
        RETURNING id, status
        """,
        job_id, worker["id"], score, round(distance_km, 2), matched_skills,
    )

    # Notify employer (fire-and-forget — don't fail apply if notif fails)
    try:
        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            SELECT ep.user_id, 'new_applicant',
                   'มีผู้สมัครงานใหม่',
                   'คะแนน Match ' || $1 || '/100'
            FROM   job_postings jp
            JOIN   employer_profiles ep ON ep.id = jp.employer_id
            WHERE  jp.id = $2
            """,
            str(int(score)), job_id,
        )
    except Exception:
        pass

    return {
        "application_id": str(app_row["id"]),
        "status":         app_row["status"],
        "match_score":    score,
        "distance_km":    round(distance_km, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


@app.get("/jobs/nearby", tags=["Matching"])
async def get_nearby_jobs(
    lat:       float,
    lng:       float,
    radius_km: float = DEFAULT_RADIUS_KM,
    user:      dict  = Depends(require_worker),
    db:        asyncpg.Connection = Depends(get_db),
):
    radius_km = min(radius_km, MAX_RADIUS_KM)

    worker = await db.fetchrow(
        "SELECT skills, daily_rate_expected FROM worker_profiles WHERE user_id=$1",
        UUID(user["sub"]),
    )
    worker_skills = worker["skills"] if worker else []
    worker_rate   = worker["daily_rate_expected"] if worker else None

    rows = await db.fetch(
        """
        SELECT
            jp.id, jp.title, jp.required_skills, jp.daily_wage_rate,
            jp.duration_days,
            jp.slots_available - jp.slots_filled AS slots_remaining,
            jp.location_name, jp.zone_name, jp.start_date,
            jp.work_start, jp.work_end, jp.ot_rate,
            ST_Y(jp.location::geometry) AS job_lat,
            ST_X(jp.location::geometry) AS job_lng,
            ST_Distance(
                ST_MakePoint($1, $2)::geography,
                jp.location
            ) / 1000.0 AS distance_km
        FROM   job_postings jp
        WHERE  jp.status = 'open'
          AND  jp.location IS NOT NULL
          AND  (jp.expires_at IS NULL OR jp.expires_at > NOW())
          AND  jp.slots_filled < jp.slots_available
          AND  ST_DWithin(
                   jp.location,
                   ST_MakePoint($1, $2)::geography,
                   $3 * 1000
               )
          AND  (
                 cardinality($4::text[]) = 0
                 OR jp.required_skills = '{}'
                 OR jp.required_skills && $4::text[]
               )
        ORDER  BY distance_km ASC
        LIMIT  50
        """,
        lng, lat, radius_km, worker_skills,
    )

    results = []
    for row in rows:
        score, matched, missing = compute_match_score(
            worker_skills   = worker_skills,
            required_skills = row["required_skills"] or [],
            distance_km     = float(row["distance_km"]),
            radius_km       = radius_km,
            worker_rate     = worker_rate,
            job_rate        = float(row["daily_wage_rate"]),
        )
        results.append({
            "job_id":          str(row["id"]),
            "title":           row["title"],
            "daily_wage_rate": float(row["daily_wage_rate"]),
            "duration_days":   row["duration_days"],
            "slots_remaining": row["slots_remaining"],
            "location_name":   row["location_name"],
            "zone_name":       row["zone_name"],
            "start_date":      str(row["start_date"]) if row["start_date"] else None,
            "work_start":      str(row["work_start"])[:5] if row["work_start"] else None,
            "work_end":        str(row["work_end"])[:5]   if row["work_end"]   else None,
            "ot_rate":         float(row["ot_rate"]) if row["ot_rate"] else None,
            "distance_km":     round(float(row["distance_km"]), 2),
            "job_lat":         float(row["job_lat"]),
            "job_lng":         float(row["job_lng"]),
            "match_score":     score,
            "matched_skills":  matched,
            "missing_skills":  missing,
        })

    results.sort(key=lambda x: (-x["match_score"], x["distance_km"]))
    return {"count": len(results), "jobs": results}


@app.get("/jobs/{job_id}/candidates", tags=["Matching"])
async def get_candidates(
    job_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    # Verify job belongs to this employer
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    job_check = await db.fetchval(
        "SELECT id FROM job_postings WHERE id=$1 AND employer_id=$2", job_id, emp_id
    )
    if not job_check:
        raise HTTPException(status_code=404, detail="ไม่พบงาน หรือไม่มีสิทธิ์ดู")

    rows = await db.fetch(
        """
        SELECT
            ja.id              AS application_id,
            wp.id              AS worker_id,
            wp.full_name,
            wp.background_check_status,
            wp.daily_rate_expected,
            ja.match_score,
            ja.distance_km,
            ja.matched_skills,
            ja.status,
            ja.checkin_at, ja.work_started_at, ja.work_ended_at, ja.employer_verified_at,
            jp.required_skills,
            jp.work_start, jp.work_end
        FROM   job_applications ja
        JOIN   worker_profiles  wp ON wp.id = ja.worker_id
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.job_id = $1
          AND  ja.status NOT IN ('rejected', 'withdrawn')
        ORDER  BY ja.match_score DESC, ja.distance_km ASC
        """,
        job_id,
    )
    return [
        {
            "application_id":          str(r["application_id"]),
            "worker_id":               str(r["worker_id"]),
            "full_name":               r["full_name"],
            "background_check_status": r["background_check_status"],
            "daily_rate_expected":     float(r["daily_rate_expected"]) if r["daily_rate_expected"] else None,
            "match_score":             float(r["match_score"] or 0),
            "distance_km":             float(r["distance_km"] or 0),
            "matched_skills":          r["matched_skills"] or [],
            "missing_skills":          list(
                set(s.lower() for s in (r["required_skills"] or [])) -
                set(s.lower() for s in (r["matched_skills"] or []))
            ),
            "status":                  r["status"],
            "checkin_at":              r["checkin_at"].isoformat() if r["checkin_at"] else None,
            "work_started_at":         r["work_started_at"].isoformat() if r["work_started_at"] else None,
            "work_ended_at":           r["work_ended_at"].isoformat() if r["work_ended_at"] else None,
            "employer_verified_at":    r["employer_verified_at"].isoformat() if r["employer_verified_at"] else None,
            "work_start":              str(r["work_start"])[:5] if r["work_start"] else None,
            "work_end":                str(r["work_end"])[:5]   if r["work_end"]   else None,
        }
        for r in rows
    ]


class DecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(hired|rejected|shortlisted)$")
    note:     Optional[str] = Field(None, max_length=500)

@app.patch("/applications/{app_id}/decide", tags=["Matching"])
async def decide_application(
    app_id: UUID,
    body:   DecisionRequest,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.job_id, ja.worker_id,
               jp.slots_available, jp.slots_filled, jp.employer_id,
               jp.title          AS job_title,
               jp.location_name,
               jp.start_date,
               jp.duration_days,
               ST_Y(jp.location::geometry) AS job_lat,
               ST_X(jp.location::geometry) AS job_lng,
               wp.full_name      AS worker_name
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id  = ja.job_id
        JOIN   worker_profiles  wp ON wp.id  = ja.worker_id
        WHERE  ja.id = $1
        """,
        app_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")

    # Verify this employer owns the job
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    if row["employer_id"] != emp_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ตัดสินใจงานนี้")

    if row["status"] not in ("applied", "shortlisted"):
        raise HTTPException(status_code=409, detail=f"ใบสมัครนี้ {row['status']} แล้ว ไม่สามารถเปลี่ยนได้")

    if body.decision == "hired" and row["slots_filled"] >= row["slots_available"]:
        raise HTTPException(status_code=409, detail="ที่นั่งเต็มแล้ว")

    async with db.transaction():
        await db.execute(
            """
            UPDATE job_applications
            SET    status = $1, employer_note = $2, decided_at = NOW()
            WHERE  id = $3
            """,
            body.decision, body.note, app_id,
        )
        if body.decision == "hired":
            await db.execute(
                """
                UPDATE job_postings
                SET    slots_filled = slots_filled + 1,
                       status = CASE WHEN slots_filled + 1 >= slots_available THEN 'filled' ELSE status END
                WHERE  id = $1
                """,
                row["job_id"],
            )
            # Auto-withdraw overlapping applications for the same worker (batch)
            if row["start_date"]:
                hired_start = row["start_date"]
                hired_end   = hired_start + timedelta(days=row["duration_days"])
                worker_name = row["worker_name"] or "Worker"

                withdrawn = await db.fetch(
                    """
                    UPDATE job_applications
                    SET    status        = 'withdrawn',
                           employer_note = 'ผู้สมัครรับงานอื่นในช่วงเวลานี้แล้ว'
                    WHERE  worker_id = $1
                      AND  status IN ('applied', 'shortlisted')
                      AND  job_id  != $2
                      AND  job_id IN (
                               SELECT id FROM job_postings
                               WHERE  start_date IS NOT NULL
                                 AND  start_date <= $3
                                 AND  start_date + duration_days >= $4
                           )
                    RETURNING job_id
                    """,
                    row["worker_id"], row["job_id"], hired_end, hired_start,
                )

                if withdrawn:
                    job_id_list = [r["job_id"] for r in withdrawn]
                    await db.execute(
                        """
                        INSERT INTO notifications (user_id, type, title, body)
                        SELECT ep.user_id,
                               'worker_unavailable',
                               'ผู้สมัครไม่พร้อมรับงาน',
                               $1 || ' รับงานอื่นในช่วงนี้แล้ว'
                        FROM   job_postings      jp
                        JOIN   employer_profiles ep ON ep.id = jp.employer_id
                        WHERE  jp.id = ANY($2::uuid[])
                        """,
                        worker_name, job_id_list,
                    )
                    logger.info(
                        f"[decide] auto-withdrawn {len(withdrawn)} overlap(s) worker={row['worker_id']}"
                    )

        notif_title = "ยินดีด้วย! คุณได้รับการคัดเลือก" if body.decision == "hired" else "ผลการสมัครงาน"

        if body.decision == "hired":
            # Generate Google Maps navigation link
            maps_link = f"https://www.google.com/maps/dir/?api=1&destination={row['job_lat']},{row['job_lng']}"
            place_name = row["location_name"] or "สถานที่ทำงาน"
            notif_body = (
                f"{body.note + ' | ' if body.note else ''}"
                f"📍 {place_name}\n"
                f"🗺️ นำทาง: {maps_link}"
            )
        else:
            notif_body = body.note or "ขออภัย ครั้งนี้ยังไม่ผ่านการคัดเลือก"

        try:
            await db.execute(
                """
                INSERT INTO notifications (user_id, type, title, body)
                SELECT wp.user_id, $1, $2, $3
                FROM   worker_profiles wp WHERE wp.id = $4
                """,
                body.decision, notif_title, notif_body, row["worker_id"],
            )
        except Exception:
            pass

    # ถ้า hired — return contact info ทันทีไม่ต้อง call ซ้ำ
    contact = None
    if body.decision == "hired":
        contact_row = await db.fetchrow(
            """
            SELECT wp.full_name, uw.phone AS worker_phone, uw.email AS worker_email
            FROM   worker_profiles wp
            JOIN   users uw ON uw.id = wp.user_id
            WHERE  wp.id = $1
            """,
            row["worker_id"],
        )
        if contact_row:
            contact = {
                "contact_name": contact_row["full_name"],
                "phone":        contact_row["worker_phone"],
                "email":        contact_row["worker_email"],
            }

    return {
        "application_id": str(app_id),
        "new_status":     body.decision,
        "contact":        contact,
    }


# ============================================================
# JOB LIFECYCLE — checkin / start / complete / verify
# ============================================================

class CheckinRequest(BaseModel):
    lat: float = Field(..., ge=-90,  le=90)
    lng: float = Field(..., ge=-180, le=180)

async def _get_app_for_worker(app_id: UUID, user: dict, db) -> dict:
    worker_id = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.job_id,
               ja.auto_confirm_start, ja.checkin_at,
               jp.title AS job_title,
               jp.work_start,
               ST_Y(jp.location::geometry) AS job_lat,
               ST_X(jp.location::geometry) AS job_lng,
               ep.user_id AS employer_user_id
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  ja.id = $1 AND ja.worker_id = $2
        """,
        app_id, worker_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")
    return row

async def _get_app_for_employer(app_id: UUID, user: dict, db) -> dict:
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.worker_id,
               ja.auto_confirm_start,
               jp.id AS job_id, jp.title AS job_title, jp.work_start,
               wp.user_id AS worker_user_id,
               ep.user_id AS employer_user_id
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        JOIN   worker_profiles  wp ON wp.id = ja.worker_id
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  ja.id = $1 AND jp.employer_id = $2
        """,
        app_id, emp_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")
    return row


@app.post("/applications/{app_id}/checkin", tags=["Job Lifecycle"])
async def worker_checkin(
    app_id: UUID,
    body:   CheckinRequest,
    user:   dict = Depends(require_worker),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Worker กด มาถึงแล้ว — ตรวจ GPS ≤ 150 เมตร"""
    row = await _get_app_for_worker(app_id, user, db)
    if row["status"] != "hired":
        raise HTTPException(status_code=409, detail=f"สถานะปัจจุบัน: {row['status']}")

    # ตรวจ GPS distance
    dist_m = await db.fetchval(
        """
        SELECT ST_Distance(
            ST_MakePoint($1, $2)::geography,
            jp.location
        )
        FROM job_applications ja
        JOIN job_postings jp ON jp.id = ja.job_id
        WHERE ja.id = $3
        """,
        body.lng, body.lat, app_id,
    )
    if dist_m is None:
        raise HTTPException(status_code=400, detail="ไม่สามารถคำนวณระยะทางได้")
    if float(dist_m) > 150:
        raise HTTPException(
            status_code=400,
            detail=f"คุณอยู่ห่างจากสถานที่งาน {round(float(dist_m))} เมตร (ต้องอยู่ในระยะ 150 เมตร)"
        )

    await db.execute(
        """
        UPDATE job_applications
        SET    status = 'checked_in', checkin_at = NOW(),
               checkin_lat = $2, checkin_lng = $3
        WHERE  id = $1
        """,
        app_id, body.lat, body.lng,
    )
    # behavioral score: jobs_hired + 1 เมื่อ worker มาจริง (ไม่ใช่แค่ employer กด hired)
    try:
        await db.execute(
            "UPDATE worker_profiles SET jobs_hired = jobs_hired + 1 WHERE user_id = $1",
            UUID(user["sub"]),
        )
        await _recompute_reliability(db, UUID(user["sub"]))
    except Exception:
        pass
    try:
        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            VALUES ($1, 'application_update', '👷 Worker มาถึงแล้ว',
                    $2)
            """,
            row["employer_user_id"],
            f"Worker เช็คอินที่ {row['job_title']} แล้ว กรุณากด 'เริ่มงาน'",
        )
    except Exception:
        pass

    # ── Auto-Confirm: employer กด toggle ล่วงหน้า → jump to working ทันที ──
    if row["auto_confirm_start"]:
        await db.execute(
            """
            UPDATE job_applications
            SET    status = 'working', work_started_at = NOW(), auto_confirmed_at = NOW()
            WHERE  id = $1
            """,
            app_id,
        )
        try:
            await db.execute(
                """
                INSERT INTO notifications (user_id, type, title, body)
                VALUES ($1, 'application_update', '▶️ เริ่มงานอัตโนมัติแล้ว', $2)
                """,
                row["employer_user_id"],
                            f"ระบบ Auto-Confirm งาน \"{row['job_title']}\" เพราะคุณรอ Employer เกิน 30 นาที — เวลานับตั้งแต่ที่คุณเช็คอิน",
            )
        except Exception:
            pass
        return {"status": "working", "auto_confirmed": True, "distance_m": round(float(dist_m))}

    return {"status": "checked_in", "distance_m": round(float(dist_m))}


@app.post("/applications/{app_id}/start", tags=["Job Lifecycle"])
async def employer_start_work(
    app_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Employer กด ยืนยันเริ่มงาน — เช็ค ±30 นาที จาก work_start"""
    from datetime import datetime, timezone, timedelta
    row = await _get_app_for_employer(app_id, user, db)
    if row["status"] != "checked_in":
        raise HTTPException(status_code=409, detail=f"Worker ยังไม่ได้เช็คอิน (สถานะ: {row['status']})")

    # Time window check (ถ้ากำหนด work_start ไว้)
    if row["work_start"]:
        TH_TZ = timezone(timedelta(hours=7))
        now_th = datetime.now(TH_TZ)
        ws = row["work_start"]
        start_min = ws.hour * 60 + ws.minute
        now_min   = now_th.hour * 60 + now_th.minute
        diff = abs(now_min - start_min)
        diff = min(diff, 1440 - diff)  # handle midnight wrap
        if diff > 30:
            raise HTTPException(
                status_code=400,
                detail=f"นอกช่วงเวลาเริ่มงาน (work_start: {ws.strftime('%H:%M')}, ตอนนี้: {now_th.strftime('%H:%M')}, ±30 นาที)"
            )

    await db.execute(
        "UPDATE job_applications SET status='working', work_started_at=NOW() WHERE id=$1",
        app_id,
    )
    try:
        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            VALUES ($1, 'application_update', '▶️ เริ่มงานแล้ว', $2)
            """,
            row["worker_user_id"],
            f"Employer ยืนยันเริ่มงาน {row['job_title']} แล้ว ขอให้โชคดี!",
        )
    except Exception:
        pass
    return {"status": "working"}


@app.post("/applications/{app_id}/auto-confirm", tags=["Job Lifecycle"])
async def toggle_auto_confirm(
    app_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Employer toggle Auto-Confirm: ถ้าเปิด → worker check-in แล้วระบบ start ทันที (ไม่ต้องกด manual)"""
    row = await _get_app_for_employer(app_id, user, db)
    if row["status"] not in ("hired", "checked_in"):
        raise HTTPException(status_code=409, detail=f"ไม่สามารถเปลี่ยนแปลงได้ (สถานะ: {row['status']})")

    new_val = not row["auto_confirm_start"]
    await db.execute(
        "UPDATE job_applications SET auto_confirm_start = $1 WHERE id = $2",
        new_val, app_id,
    )

    # ถ้าเปิด auto-confirm และ worker checked_in อยู่แล้ว → start ทันที
    if new_val and row["status"] == "checked_in":
        await db.execute(
            """
            UPDATE job_applications
            SET    status = 'working', work_started_at = NOW(), auto_confirmed_at = NOW()
            WHERE  id = $1
            """,
            app_id,
        )
        try:
            await db.execute(
                """
                INSERT INTO notifications (user_id, type, title, body)
                VALUES ($1, 'application_update', '▶️ เริ่มงานอัตโนมัติแล้ว', $2)
                """,
                row["worker_user_id"],
                f"Employer เปิด Auto-Confirm — งาน {row['job_title']} เริ่มนับเวลาแล้ว",
            )
        except Exception:
            pass
        return {"auto_confirm_start": True, "status": "working", "message": "Auto-Confirm เปิดแล้ว และเริ่มงานทันทีเพราะ Worker เช็คอินแล้ว"}

    return {
        "auto_confirm_start": new_val,
        "status": row["status"],
        "message": "Auto-Confirm เปิดแล้ว — ระบบจะ start อัตโนมัติเมื่อ Worker เช็คอิน" if new_val else "Auto-Confirm ปิดแล้ว",
    }


@app.post("/applications/{app_id}/complete", tags=["Job Lifecycle"])
async def worker_complete(
    app_id: UUID,
    user:   dict = Depends(require_worker),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Worker กด งานเสร็จแล้ว"""
    row = await _get_app_for_worker(app_id, user, db)
    if row["status"] != "working":
        raise HTTPException(status_code=409, detail=f"สถานะปัจจุบัน: {row['status']}")

    await db.execute(
        "UPDATE job_applications SET status='completed', work_ended_at=NOW() WHERE id=$1",
        app_id,
    )
    try:
        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            VALUES ($1, 'application_update', '✅ Worker แจ้งงานเสร็จ', $2)
            """,
            row["employer_user_id"],
            f"Worker แจ้งเสร็จงาน {row['job_title']} แล้ว กรุณากด 'ยืนยันจบงาน'",
        )
    except Exception:
        pass
    return {"status": "completed"}


@app.post("/applications/{app_id}/verify", tags=["Job Lifecycle"])
async def employer_verify_complete(
    app_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Employer กด ยืนยันจบงาน → trigger ให้ทั้งคู่ไป review"""
    row = await _get_app_for_employer(app_id, user, db)
    if row["status"] != "completed":
        raise HTTPException(status_code=409, detail=f"Worker ยังไม่ได้แจ้งเสร็จงาน (สถานะ: {row['status']})")

    await db.execute(
        "UPDATE job_applications SET status='verified', employer_verified_at=NOW() WHERE id=$1",
        app_id,
    )
    # ถ้า slots เต็มแล้ว → mark job เป็น filled
    await db.execute(
        """
        UPDATE job_postings SET status='filled'
        WHERE  id=$1 AND status='open'
          AND  slots_filled >= slots_available
        """,
        row["job_id"],
    )
    review_msg = f"งาน {row['job_title']} เสร็จสิ้นแล้ว! กรุณาให้คะแนนและรีวิว"
    try:
        # Notify worker
        await db.execute(
            "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'review_pending', '⭐ ให้คะแนนงาน', $2)",
            row["worker_user_id"], review_msg,
        )
        # Notify employer (ตัวเอง)
        emp_user_id = UUID(user["sub"])
        await db.execute(
            "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'review_pending', '⭐ ให้คะแนน Worker', $2)",
            emp_user_id, review_msg,
        )
    except Exception:
        pass
    return {"status": "verified"}


# ============================================================
# ANTI-GHOSTING — Backup Workers & No-Show
# ============================================================

@app.get("/jobs/{job_id}/backup-workers", tags=["Anti-Ghosting"])
async def get_backup_workers(
    job_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Employer ดู top backup candidates สำหรับงานนี้ (applied/shortlisted ที่ยังไม่ hired)"""
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    job_check = await db.fetchval(
        "SELECT id FROM job_postings WHERE id=$1 AND employer_id=$2", job_id, emp_id
    )
    if not job_check:
        raise HTTPException(status_code=404, detail="ไม่พบงาน หรือไม่มีสิทธิ์ดู")

    rows = await db.fetch(
        """
        SELECT
            ja.id              AS application_id,
            wp.id              AS worker_id,
            wp.full_name,
            wp.background_check_status,
            wp.daily_rate_expected,
            ja.match_score,
            ja.distance_km,
            ja.matched_skills,
            ja.status,
            ja.backup_priority,
            ja.backup_offered_at,
            ja.backup_accepted_at
        FROM   job_applications ja
        JOIN   worker_profiles  wp ON wp.id = ja.worker_id
        WHERE  ja.job_id = $1
          AND  ja.status IN ('applied', 'shortlisted')
        ORDER  BY ja.match_score DESC, ja.distance_km ASC
        LIMIT  10
        """,
        job_id,
    )
    return [
        {
            "application_id":          str(r["application_id"]),
            "worker_id":               str(r["worker_id"]),
            "full_name":               r["full_name"],
            "background_check_status": r["background_check_status"],
            "daily_rate_expected":     float(r["daily_rate_expected"]) if r["daily_rate_expected"] else None,
            "match_score":             float(r["match_score"] or 0),
            "distance_km":             float(r["distance_km"] or 0),
            "matched_skills":          r["matched_skills"] or [],
            "status":                  r["status"],
            "backup_priority":         r["backup_priority"],
            "backup_offered_at":       r["backup_offered_at"].isoformat() if r["backup_offered_at"] else None,
            "backup_accepted_at":      r["backup_accepted_at"].isoformat() if r["backup_accepted_at"] else None,
        }
        for r in rows
    ]



async def _recompute_reliability(db, worker_user_id):
    """Recompute reliability_score จาก jobs_completed, jobs_noshow, jobs_hired, review avg"""
    row = await db.fetchrow(
        """
        SELECT wp.jobs_completed, wp.jobs_noshow, wp.jobs_hired,
               COALESCE(wrs.avg_rating, 5.0) AS review_avg
        FROM   worker_profiles wp
        LEFT JOIN worker_review_summary wrs ON wrs.worker_id = wp.id
        WHERE  wp.user_id = $1
        """,
        worker_user_id,
    )
    if not row:
        return
    total    = max(row["jobs_hired"], 1)
    cr       = min(row["jobs_completed"] / total, 1.0)
    nr       = min(row["jobs_noshow"]    / total, 1.0)
    rv       = float(row["review_avg"] or 5.0) / 5.0
    score    = round((cr * 5.0) + ((1.0 - nr) * 3.0) + (rv * 2.0), 2)
    await db.execute(
        """
        UPDATE worker_profiles
        SET reliability_score = $1, score_updated_at = NOW()
        WHERE user_id = $2
        """,
        score, worker_user_id,
    )

# ── Helper: cascade backup offer ไปยัง worker ที่ใกล้สุด ────────────────────
async def _cascade_backup_offer(
    db, job_id, wage_amount, wage_hours, job_title, auto_confirmed: bool = False
):
    """ส่ง backup offer ไปยัง worker ที่ available และใกล้งานสุด"""
    # mark job ว่า wage confirmed แล้ว
    await db.execute(
        """
        UPDATE job_postings
        SET backup_wage_pending      = FALSE,
            backup_wage_confirmed_at = NOW()
        WHERE id = $1
        """,
        job_id,
    )
    # หา backup worker ที่ใกล้สุดและยังไม่ได้รับ offer
    backup = await db.fetchrow(
        """
        SELECT ja.id          AS app_id,
               wp.user_id     AS worker_user_id
        FROM   job_applications ja
        JOIN   worker_profiles  wp ON wp.id = ja.worker_id
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.job_id            = $1
          AND  ja.status           IN ('applied', 'shortlisted')
          AND  ja.backup_offered_at IS NULL
          AND  wp.location         IS NOT NULL
        ORDER  BY ST_Distance(wp.location, jp.location) ASC
        LIMIT  1
        """,
        job_id,
    )
    if not backup:
        return  # ไม่มี backup available
    next_priority = await db.fetchval(
        "SELECT COALESCE(MAX(backup_priority), 0) + 1 FROM job_applications WHERE job_id=$1",
        job_id,
    )
    await db.execute(
        """
        UPDATE job_applications
        SET backup_priority        = $1,
            backup_offered_at      = NOW(),
            backup_confirmed_wage  = $2
        WHERE id = $3
        """,
        next_priority, wage_amount, backup["app_id"],
    )
    wage_str  = f"{wage_amount:,.0f}" if wage_amount else "?"
    hours_str = f"{wage_hours:.1f}"  if wage_hours  else "?"
    label     = "อัตโนมัติ" if auto_confirmed else "ยืนยันโดย Employer"
    await db.execute(
        """
        INSERT INTO notifications (user_id, type, title, body)
        VALUES ($1, 'application_update', '🔴 งานด่วน! มีตำแหน่งว่างตอนนี้', $2)
        """,
        backup["worker_user_id"],
        f"งาน \"{job_title}\" มีตำแหน่งว่างกะทันหัน\n"
        f"เวลาที่เหลือ: {hours_str} ชม. | ค่าจ้าง: {wage_str}฿ ({label})\n"
        f"ตอบรับภายใน 5 นาที ไม่งั้นระบบจะเสนองานให้คนถัดไป",
    )


@app.post("/jobs/{job_id}/confirm-backup-wage", tags=["Anti-Ghosting"])
async def confirm_backup_wage(
    job_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Employer ยืนยันค่าจ้าง pro-rata ก่อนส่ง backup offer"""
    employer_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        """
        SELECT id, title, backup_wage_pending, backup_wage_amount,
               backup_wage_hours, backup_wage_confirmed_at
        FROM   job_postings
        WHERE  id = $1 AND employer_id = $2
        """,
        job_id, employer_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบงาน")
    if not row["backup_wage_pending"]:
        raise HTTPException(status_code=400, detail="ไม่มี backup wage รอยืนยัน")
    if row["backup_wage_confirmed_at"] is not None:
        raise HTTPException(status_code=409, detail="ยืนยันไปแล้ว")
    async with db.transaction():
        await _cascade_backup_offer(
            db, job_id,
            row["backup_wage_amount"], row["backup_wage_hours"],
            row["title"], auto_confirmed=False,
        )
    return {
        "status": "backup_cascaded",
        "wage_amount": float(row["backup_wage_amount"]) if row["backup_wage_amount"] else None,
        "wage_hours":  float(row["backup_wage_hours"])  if row["backup_wage_hours"]  else None,
        "message":     "ส่ง offer ไปยัง Worker สำรองที่ใกล้ที่สุดแล้ว",
    }


@app.post("/applications/{app_id}/send-backup", tags=["Anti-Ghosting"])
async def send_backup_offer(
    app_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Employer ส่ง backup offer ไปหา worker ที่ยังไม่ hired (เมื่อ hired worker no-show)"""
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.job_id, ja.worker_id, ja.backup_offered_at,
               jp.title AS job_title, jp.employer_id
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.id = $1
        """,
        app_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")
    if row["employer_id"] != emp_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์")
    if row["status"] not in ("applied", "shortlisted"):
        raise HTTPException(
            status_code=409,
            detail=f"ส่ง backup offer ได้เฉพาะ applied/shortlisted (สถานะปัจจุบัน: {row['status']})",
        )
    if row["backup_offered_at"] is not None:
        raise HTTPException(status_code=409, detail="ส่ง backup offer ไปแล้ว รอ worker ตอบรับ")

    next_priority = await db.fetchval(
        "SELECT COALESCE(MAX(backup_priority), 0) + 1 FROM job_applications WHERE job_id=$1",
        row["job_id"],
    )
    await db.execute(
        "UPDATE job_applications SET backup_priority=$1, backup_offered_at=NOW() WHERE id=$2",
        next_priority, app_id,
    )

    worker_user_id = await db.fetchval(
        "SELECT user_id FROM worker_profiles WHERE id=$1", row["worker_id"]
    )
    try:
        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            VALUES ($1, 'hired', '🆕 มีงานพิเศษสำหรับคุณ!', $2)
            """,
            worker_user_id,
            f"Employer เสนองาน \"{row['job_title']}\" ให้คุณด่วน! "
            f"(Worker เดิมไม่มา) กรุณาตอบรับภายใน 30 นาที",
        )
    except Exception:
        pass

    return {"status": "backup_offered", "backup_priority": next_priority}


@app.post("/applications/{app_id}/accept-backup", tags=["Anti-Ghosting"])
async def accept_backup_offer(
    app_id: UUID,
    user:   dict = Depends(require_worker),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Worker กด รับงานสำรอง → status เปลี่ยนเป็น hired"""
    worker_id = await db.fetchval(
        "SELECT id FROM worker_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.job_id,
               ja.backup_offered_at, ja.backup_accepted_at,
               jp.title          AS job_title,
               jp.slots_available, jp.slots_filled,
               jp.location_name,
               ST_Y(jp.location::geometry) AS job_lat,
               ST_X(jp.location::geometry) AS job_lng,
               ep.user_id        AS employer_user_id
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  ja.id = $1 AND ja.worker_id = $2
        """,
        app_id, worker_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")
    if row["backup_offered_at"] is None:
        raise HTTPException(status_code=400, detail="ยังไม่ได้รับ backup offer")
    if row["backup_accepted_at"] is not None:
        raise HTTPException(status_code=409, detail="รับงานนี้ไปแล้ว")
    if row["status"] == "hired":
        raise HTTPException(status_code=409, detail="ได้รับสถานะ hired แล้ว")
    if row["slots_filled"] >= row["slots_available"]:
        raise HTTPException(status_code=409, detail="ที่นั่งเต็มแล้ว")

    maps_link  = f"https://www.google.com/maps/dir/?api=1&destination={row['job_lat']},{row['job_lng']}"
    place_name = row["location_name"] or "สถานที่ทำงาน"

    async with db.transaction():
        await db.execute(
            """
            UPDATE job_applications
            SET    status = 'hired', backup_accepted_at = NOW(), decided_at = NOW()
            WHERE  id = $1
            """,
            app_id,
        )
        await db.execute(
            """
            UPDATE job_postings
            SET    slots_filled = slots_filled + 1,
                   status = CASE WHEN slots_filled + 1 >= slots_available THEN 'filled' ELSE status END
            WHERE  id = $1
            """,
            row["job_id"],
        )
        await db.execute(
            """
            INSERT INTO notifications (user_id, type, title, body)
            VALUES ($1, 'hired', '✅ คุณได้รับงานสำรอง!', $2)
            """,
            UUID(user["sub"]),
            f"ยินดีด้วย! คุณได้รับงาน \"{row['job_title']}\"\n📍 {place_name}\n🗺️ นำทาง: {maps_link}",
        )
        worker_name = await db.fetchval(
            "SELECT full_name FROM worker_profiles WHERE id=$1", worker_id
        )
        try:
            await db.execute(
                """
                INSERT INTO notifications (user_id, type, title, body)
                VALUES ($1, 'new_applicant', '✅ Worker สำรองตอบรับแล้ว', $2)
                """,
                row["employer_user_id"],
                f"Worker {worker_name} ตอบรับงาน \"{row['job_title']}\" แล้ว เตรียมรับ Worker ได้เลย",
            )
        except Exception:
            pass

    return {"status": "hired", "job_title": row["job_title"]}


@app.patch("/applications/{app_id}/mark-noshow", tags=["Anti-Ghosting"])
async def mark_noshow(
    app_id: UUID,
    user:   dict = Depends(require_employer),
    db:     asyncpg.Connection = Depends(get_db),
):
    """Employer mark worker ว่าไม่มาทำงาน → status = no_show + คืน slot"""
    emp_id = await db.fetchval(
        "SELECT id FROM employer_profiles WHERE user_id=$1", UUID(user["sub"])
    )
    row = await db.fetchrow(
        """
        SELECT ja.id, ja.status, ja.job_id, ja.worker_id,
               jp.title AS job_title, jp.employer_id
        FROM   job_applications ja
        JOIN   job_postings     jp ON jp.id = ja.job_id
        WHERE  ja.id = $1
        """,
        app_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")
    if row["employer_id"] != emp_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์")
    if row["status"] != "hired":
        raise HTTPException(
            status_code=409,
            detail=f"mark no-show ได้เฉพาะ status=hired (ปัจจุบัน: {row['status']})",
        )

    async with db.transaction():
        await db.execute(
            "UPDATE job_applications SET status='no_show', noshow_marked_at=NOW() WHERE id=$1",
            app_id,
        )
        await db.execute(
            "UPDATE job_postings SET slots_filled = GREATEST(0, slots_filled - 1) WHERE id=$1",
            row["job_id"],
        )
        worker_user_id = await db.fetchval(
            "SELECT user_id FROM worker_profiles WHERE id=$1", row["worker_id"]
        )
        try:
            await db.execute(
                """
                INSERT INTO notifications (user_id, type, title, body)
                VALUES ($1, 'application_update', '❌ ถูกทำเครื่องหมาย No-Show', $2)
                """,
                worker_user_id,
                f"Employer ทำเครื่องหมายว่าคุณไม่มาทำงาน \"{row['job_title']}\" "
                f"หากมีข้อผิดพลาด กรุณาติดต่อทีมงาน",
            )
        except Exception:
            pass

    return {"status": "no_show", "job_title": row["job_title"]}


# ============================================================
# JOB CATEGORIES & TITLES (Master Data)
# ============================================================

@app.get("/job-categories", tags=["Master Data"])
async def get_job_categories(db: asyncpg.Connection = Depends(get_db)):
    rows = await db.fetch(
        "SELECT id, code, name_th, icon FROM job_categories ORDER BY sort_order"
    )
    return [dict(r) for r in rows]

@app.get("/job-categories/{category_code}/titles", tags=["Master Data"])
async def get_job_titles(
    category_code: str,
    db: asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT jt.id, jt.code, jt.name_th
        FROM   job_titles jt
        JOIN   job_categories jc ON jc.id = jt.category_id
        WHERE  jc.code = $1
        ORDER  BY jt.sort_order
        """,
        category_code,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="ไม่พบ category นี้")
    return [dict(r) for r in rows]

@app.get("/zones", tags=["Master Data"])
async def get_zones(db: asyncpg.Connection = Depends(get_db)):
    rows = await db.fetch(
        "SELECT code, name_th FROM zones WHERE is_active = TRUE ORDER BY name_th"
    )
    return [dict(r) for r in rows]


# ============================================================
# CONTACT REVEAL — เปิดเผยเบอร์โทรเฉพาะคู่ที่ hired แล้ว
# ============================================================

@app.get("/applications/{app_id}/contact", tags=["Matching"])
async def get_contact(
    app_id: UUID,
    user:   dict = Depends(get_current_user),
    db:     asyncpg.Connection = Depends(get_db),
):
    user_id = UUID(user["sub"])
    role    = user["role"]

    row = await db.fetchrow(
        """
        SELECT
            ja.status,
            ja.worker_id,
            wp.user_id  AS worker_user_id,
            ep.user_id  AS employer_user_id,
            jp.title    AS job_title,
            -- worker info
            wp.full_name,
            uw.phone    AS worker_phone,
            uw.email    AS worker_email,
            -- employer info
            ep.company_name,
            ep.contact_person,
            ue.phone    AS employer_phone,
            ue.email    AS employer_email
        FROM   job_applications ja
        JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
        JOIN   users             uw ON uw.id  = wp.user_id
        JOIN   job_postings      jp ON jp.id  = ja.job_id
        JOIN   employer_profiles ep ON ep.id  = jp.employer_id
        JOIN   users             ue ON ue.id  = ep.user_id
        WHERE  ja.id = $1
        """,
        app_id,
    )

    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบใบสมัคร")

    # อนุญาตตลอดช่วงงาน active (hired → verified)
    _CONTACT_OK = {"hired", "checked_in", "working", "completed", "verified"}
    if row["status"] not in _CONTACT_OK:
        raise HTTPException(status_code=403, detail="เปิดเผยข้อมูลติดต่อได้เฉพาะงานที่ active แล้วเท่านั้น")

    # ตรวจสิทธิ์ — ต้องเป็นคู่ที่เกี่ยวข้องกัน
    if role == "worker" and row["worker_user_id"] != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดูข้อมูลนี้")
    if role == "employer" and row["employer_user_id"] != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดูข้อมูลนี้")

    # Worker เห็นข้อมูล Employer / Employer เห็นข้อมูล Worker
    if role == "worker":
        return {
            "job_title":    row["job_title"],
            "contact_name": row["contact_person"],
            "company_name": row["company_name"],
            "phone":        row["employer_phone"],
            "email":        row["employer_email"],
        }
    else:
        return {
            "job_title":    row["job_title"],
            "contact_name": row["full_name"],
            "phone":        row["worker_phone"],
            "email":        row["worker_email"],
        }


# ============================================================
# NOTIFICATIONS
# ============================================================

@app.get("/notifications", tags=["Notifications"])
async def get_notifications(
    limit:  int  = 20,
    unread: bool = False,
    user:   dict = Depends(get_current_user),
    db:     asyncpg.Connection = Depends(get_db),
):
    query = """
        SELECT id, type, title, body, is_read, created_at
        FROM   notifications
        WHERE  user_id = $1
    """
    params = [UUID(user["sub"])]
    if unread:
        query += " AND is_read = FALSE"
    query += " ORDER BY created_at DESC LIMIT $2"
    params.append(limit)

    rows = await db.fetch(query, *params)
    return [
        {
            "id":         str(r["id"]),
            "type":       r["type"],
            "title":      r["title"],
            "body":       r["body"],
            "is_read":    r["is_read"],
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]

@app.get("/notifications/unread-count", tags=["Notifications"])
async def get_unread_count(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    count = await db.fetchval(
        "SELECT COUNT(*) FROM notifications WHERE user_id=$1 AND is_read=FALSE",
        UUID(user["sub"]),
    )
    return {"count": int(count)}

@app.patch("/notifications/read-all", tags=["Notifications"])
async def mark_all_read(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    await db.execute(
        "UPDATE notifications SET is_read=TRUE WHERE user_id=$1 AND is_read=FALSE",
        UUID(user["sub"]),
    )
    return {"status": "ok"}

@app.patch("/notifications/{notif_id}/read", tags=["Notifications"])
async def mark_read(
    notif_id: UUID,
    user:     dict = Depends(get_current_user),
    db:       asyncpg.Connection = Depends(get_db),
):
    await db.execute(
        "UPDATE notifications SET is_read=TRUE WHERE id=$1 AND user_id=$2",
        notif_id, UUID(user["sub"]),
    )
    return {"status": "ok"}


# ============================================================
# REVIEW SUMMARY
# ============================================================

@app.get("/workers/{worker_user_id}/review-summary", tags=["Reviews"])
async def get_worker_review_summary(
    worker_user_id: UUID,
    db: asyncpg.Connection = Depends(get_db),
):
    """Public summary — แสดงบน profile card"""
    row = await db.fetchrow(
        """
        SELECT
            COUNT(r.id)                                          AS total_reviews,
            ROUND(AVG(r.star_rating), 1)                        AS avg_stars,
            COUNT(r.id) FILTER (WHERE r.would_rehire = TRUE)    AS rehire_count,
            ARRAY_AGG(rt.tag_label ORDER BY cnt DESC)           AS top_tags
        FROM reviews r
        LEFT JOIN LATERAL (
            SELECT rt.tag_label, COUNT(*) AS cnt
            FROM   review_tag_selections rts
            JOIN   review_tags rt ON rt.id = rts.tag_id
            WHERE  rts.review_id = r.id
            GROUP  BY rt.tag_label
            ORDER  BY cnt DESC
            LIMIT  3
        ) rt ON TRUE
        WHERE  r.reviewee_id  = $1
          AND  r.is_visible   = TRUE
          AND  r.reviewer_role = 'employer'
        """,
        worker_user_id,
    )

    if not row or not row["total_reviews"]:
        return {"total_reviews": 0, "avg_stars": None, "rehire_pct": None, "top_tags": []}

    total     = int(row["total_reviews"])
    rehire    = int(row["rehire_count"] or 0)
    return {
        "total_reviews": total,
        "avg_stars":     float(row["avg_stars"]) if row["avg_stars"] else None,
        "rehire_pct":    round(rehire / total * 100) if total else None,
        "top_tags":      [t for t in (row["top_tags"] or []) if t][:3],
    }

@app.get("/employers/{employer_user_id}/review-summary", tags=["Reviews"])
async def get_employer_review_summary(
    employer_user_id: UUID,
    db: asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT
            COUNT(r.id)                  AS total_reviews,
            ROUND(AVG(r.star_rating), 1) AS avg_stars
        FROM reviews r
        WHERE  r.reviewee_id   = $1
          AND  r.is_visible    = TRUE
          AND  r.reviewer_role = 'worker'
        """,
        employer_user_id,
    )
    if not row or not row["total_reviews"]:
        return {"total_reviews": 0, "avg_stars": None}
    return {
        "total_reviews": int(row["total_reviews"]),
        "avg_stars":     float(row["avg_stars"]) if row["avg_stars"] else None,
    }


# ============================================================
# BACKGROUND CHECK (Mock flow)
# ============================================================

@app.post("/workers/background-check/request", tags=["Trust & Safety"])
async def request_background_check(
    user: dict = Depends(require_worker),
    db:   asyncpg.Connection = Depends(get_db),
):
    """Worker ส่งคำขอ background check — รอ admin อนุมัติ"""
    worker = await db.fetchrow(
        "SELECT id, background_check_status FROM worker_profiles WHERE user_id=$1",
        UUID(user["sub"]),
    )
    if not worker:
        raise HTTPException(status_code=404, detail="สร้าง Worker Profile ก่อน")
    if worker["background_check_status"] == "verified":
        raise HTTPException(status_code=409, detail="ผ่านการตรวจสอบแล้ว")
    if worker["background_check_status"] == "pending":
        raise HTTPException(status_code=409, detail="รออยู่ระหว่างการตรวจสอบแล้ว")

    await db.execute(
        "UPDATE worker_profiles SET background_check_status='pending' WHERE id=$1",
        worker["id"],
    )
    return {"status": "pending", "message": "ส่งคำขอแล้ว รอ admin อนุมัติ"}


@app.post("/admin/cron/trigger", tags=["Admin"], include_in_schema=False)
async def trigger_cron(x_admin_secret: str = Header(default="")):
    """Test-only: manually trigger auto_verify + check_expired_jobs crons (guarded by admin_secret)"""
    if not settings.admin_secret or x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    await auto_verify_completed_jobs()
    await check_expired_jobs()
    return {"ok": True}


# ── Public Stats (landing page) ────────────────────────────

@app.get("/public/stats", tags=["Public"])
async def public_stats(db: asyncpg.Connection = Depends(get_db)):
    """Stats สาธารณะสำหรับ landing page — ไม่ต้อง auth"""
    row = await db.fetchrow("""
        SELECT
            (SELECT COUNT(*) FROM users WHERE role='worker')         AS total_workers,
            (SELECT COUNT(*) FROM users WHERE role='employer')       AS total_employers,
            (SELECT COUNT(*) FROM job_postings WHERE status='open')  AS jobs_open
    """)
    return dict(row)


# ── Admin Dashboard ────────────────────────────────────────

@app.get("/admin/stats", tags=["Admin"])
async def admin_stats(
    user: dict = Depends(require_admin),
    db:   asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow("""
        SELECT
            (SELECT COUNT(*) FROM users WHERE role='worker')              AS total_workers,
            (SELECT COUNT(*) FROM users WHERE role='employer')            AS total_employers,
            (SELECT COUNT(*) FROM job_postings WHERE status='open')       AS jobs_open,
            (SELECT COUNT(*) FROM job_postings WHERE status='closed')     AS jobs_closed,
            (SELECT COUNT(*) FROM job_postings WHERE status='filled')     AS jobs_filled,
            (SELECT COUNT(*) FROM job_applications)                       AS total_applications,
            (SELECT COUNT(*) FROM job_applications
             WHERE  status = 'hired' AND decided_at >= NOW()::date)       AS hired_today,
            (SELECT COUNT(*) FROM job_applications WHERE status='disputed') AS open_disputes,
            (SELECT COUNT(*) FROM worker_profiles
             WHERE  background_check_status='pending')                    AS kyc_pending,
            (SELECT COUNT(*) FROM job_applications WHERE status='verified') AS total_completed,
            (SELECT COUNT(*) FROM job_applications
             WHERE  status IN ('hired','checked_in','working','completed','verified')) AS total_hired_alltime,
            (SELECT ROUND(
                COUNT(*) FILTER (WHERE status='verified') * 100.0 /
                NULLIF(COUNT(*) FILTER (WHERE status IN ('hired','checked_in','working','completed','verified','no_show')), 0)
            , 1) FROM job_applications)                                    AS completion_rate_pct,
            (SELECT ROUND(EXTRACT(EPOCH FROM AVG(decided_at - jp.created_at))/3600, 1)
             FROM   job_applications ja
             JOIN   job_postings jp ON jp.id = ja.job_id
             WHERE  ja.status = 'hired' AND ja.decided_at IS NOT NULL)    AS avg_time_to_hire_hours,
            (SELECT COUNT(*) FROM users WHERE created_at >= NOW()::date)  AS new_users_today,
            (SELECT COUNT(*) FROM job_postings
             WHERE  created_at >= NOW()::date)                            AS jobs_posted_today
    """)
    return dict(row)


@app.get("/admin/users", tags=["Admin"])
async def admin_list_users(
    role:   Optional[str] = None,
    status: Optional[str] = None,
    page:   int = 1,
    user:   dict = Depends(require_admin),
    db:     asyncpg.Connection = Depends(get_db),
):
    conditions = ["u.role != 'admin'"]
    params: list = []
    if role in ("worker", "employer"):
        params.append(role)
        conditions.append(f"u.role = ${len(params)}")
    if status == "active":
        conditions.append("u.is_active = true")
    elif status in ("suspended", "banned"):
        conditions.append("u.is_active = false")
    offset = (page - 1) * 20
    params += [20, offset]
    where = " AND ".join(conditions)
    rows = await db.fetch(f"""
        SELECT u.id, u.email, u.phone, u.role, u.is_active, u.created_at,
               COALESCE(wp.full_name, ep.company_name) AS name
        FROM   users u
        LEFT JOIN worker_profiles   wp ON wp.user_id = u.id
        LEFT JOIN employer_profiles ep ON ep.user_id = u.id
        WHERE  {where}
        ORDER  BY u.created_at DESC
        LIMIT  ${len(params) - 1} OFFSET ${len(params)}
    """, *params)
    return [dict(r) for r in rows]


@app.patch("/admin/users/{target_user_id}/status", tags=["Admin"])
async def admin_update_user_status(
    target_user_id: UUID,
    body: AdminUserStatus,
    user: dict = Depends(require_admin),
    db:   asyncpg.Connection = Depends(get_db),
):
    await db.execute(
        "UPDATE users SET is_active=$1 WHERE id=$2",
        body.status == "active", target_user_id,
    )
    return {"user_id": str(target_user_id), "status": body.status}


@app.get("/admin/kyc/pending", tags=["Admin"])
async def admin_kyc_pending(
    user: dict = Depends(require_admin),
    db:   asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch("""
        SELECT wp.id, wp.user_id, wp.full_name, wp.background_check_status,
               wp.kyc_submitted_at, wp.nationality_type, wp.kyc_note,
               wp.face_photo_url, wp.id_card_photo_url,
               u.email
        FROM   worker_profiles wp
        JOIN   users u ON u.id = wp.user_id
        WHERE  wp.background_check_status = 'pending'
        ORDER  BY wp.kyc_submitted_at ASC NULLS LAST
    """)
    result = []
    for r in rows:
        item = dict(r)
        item["face_signed_url"]    = await _storage_signed_url(r["face_photo_url"]    or "")
        item["id_card_signed_url"] = await _storage_signed_url(r["id_card_photo_url"] or "")
        result.append(item)
    return result


@app.patch("/admin/kyc/{worker_id}/review", tags=["Admin"])
async def admin_kyc_review(
    worker_id: UUID,
    body:      AdminKYCReview,
    user:      dict = Depends(require_admin),
    db:        asyncpg.Connection = Depends(get_db),
):
    worker = await db.fetchrow(
        "SELECT id, user_id FROM worker_profiles WHERE id=$1", worker_id
    )
    if not worker:
        raise HTTPException(status_code=404, detail="ไม่พบ Worker")
    await db.execute(
        """
        UPDATE worker_profiles
        SET    background_check_status = $1,
               kyc_reviewed_at = NOW(),
               kyc_reviewed_by = $2,
               kyc_note        = $3
        WHERE  id = $4
        """,
        body.decision, UUID(user["sub"]), body.note, worker_id,
    )
    notif_title = "✅ KYC ผ่านการยืนยันแล้ว" if body.decision == "verified" else "❌ KYC ไม่ผ่าน"
    notif_body  = body.note or (
        "โปรไฟล์ของคุณได้รับ Badge KYC Verified แล้ว" if body.decision == "verified"
        else "เอกสารไม่ผ่านการตรวจสอบ กรุณาอัปโหลดใหม่"
    )
    await db.execute(
        "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'kyc_review', $2, $3)",
        worker["user_id"], notif_title, notif_body,
    )
    return {"worker_id": str(worker_id), "status": body.decision}


@app.get("/admin/disputes", tags=["Admin"])
async def admin_list_disputes(
    user: dict = Depends(require_admin),
    db:   asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch("""
        SELECT ja.id, ja.status, ja.employer_note, ja.work_started_at, ja.work_ended_at,
               jp.title        AS job_title,    jp.daily_wage_rate,
               wp.full_name    AS worker_name,  wu.email AS worker_email,
               ep.company_name,                 eu.id    AS employer_user_id,
               wu.id           AS worker_user_id
        FROM   job_applications  ja
        JOIN   job_postings      jp ON jp.id  = ja.job_id
        JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
        JOIN   users             wu ON wu.id  = wp.user_id
        JOIN   employer_profiles ep ON ep.id  = jp.employer_id
        JOIN   users             eu ON eu.id  = ep.user_id
        WHERE  ja.status = 'disputed'
        ORDER  BY ja.work_ended_at DESC NULLS LAST
    """)
    return [dict(r) for r in rows]


@app.patch("/admin/disputes/{dispute_id}/resolve", tags=["Admin"])
async def admin_resolve_dispute(
    dispute_id: UUID,
    body:       AdminDisputeResolve,
    user:       dict = Depends(require_admin),
    db:         asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """
        SELECT ja.id, wp.user_id AS worker_uid, eu.id AS employer_uid
        FROM   job_applications  ja
        JOIN   job_postings      jp ON jp.id  = ja.job_id
        JOIN   worker_profiles   wp ON wp.id  = ja.worker_id
        JOIN   employer_profiles ep ON ep.id  = jp.employer_id
        JOIN   users             eu ON eu.id  = ep.user_id
        WHERE  ja.id = $1 AND ja.status = 'disputed'
        """,
        dispute_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบ dispute หรือ status ไม่ใช่ disputed")
    winner      = "Worker" if body.decision == "worker_win" else "Employer"
    outcome_note = f"[Admin: {winner} ชนะ] {body.note or ''}"
    await db.execute(
        "UPDATE job_applications SET status='verified', employer_note=$1 WHERE id=$2",
        outcome_note, dispute_id,
    )
    notif_msg = f"Admin ตัดสิน: {winner} ชนะ — {body.note or ''}"
    for uid in (row["worker_uid"], row["employer_uid"]):
        await db.execute(
            "INSERT INTO notifications (user_id, type, title, body) VALUES ($1, 'dispute_resolved', '⚖️ Admin ตัดสินแล้ว', $2)",
            uid, notif_msg,
        )
    return {"dispute_id": str(dispute_id), "decision": body.decision}


@app.get("/admin/jobs", tags=["Admin"])
async def admin_list_jobs(
    status: Optional[str] = None,
    page:   int = 1,
    user:   dict = Depends(require_admin),
    db:     asyncpg.Connection = Depends(get_db),
):
    params: list = []
    where = "1=1"
    if status:
        params.append(status)
        where = f"jp.status = ${len(params)}"
    offset = (page - 1) * 20
    params += [20, offset]
    rows = await db.fetch(f"""
        SELECT jp.id, jp.title, jp.status, jp.daily_wage_rate, jp.duration_days,
               jp.slots_available, jp.slots_filled, jp.location_name,
               jp.start_date,      jp.created_at,
               ep.company_name
        FROM   job_postings      jp
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  {where}
        ORDER  BY jp.created_at DESC
        LIMIT  ${len(params) - 1} OFFSET ${len(params)}
    """, *params)
    return [dict(r) for r in rows]


@app.patch("/admin/jobs/{job_id}/status", tags=["Admin"])
async def admin_update_job_status(
    job_id: UUID,
    body:   AdminJobStatus,
    user:   dict = Depends(require_admin),
    db:     asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow("SELECT id FROM job_postings WHERE id=$1", job_id)
    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบงาน")
    await db.execute("UPDATE job_postings SET status=$1 WHERE id=$2", body.status, job_id)
    return {"job_id": str(job_id), "status": body.status}


@app.patch("/admin/workers/{worker_user_id}/verify", tags=["Admin"])
async def admin_verify_worker(
    worker_user_id: UUID,
    x_admin_secret: str = Header(default=""),
    db: asyncpg.Connection = Depends(get_db),
):
    """Admin อนุมัติ background check ของ worker"""
    if not settings.admin_secret or x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์")

    worker = await db.fetchrow(
        "SELECT id, user_id FROM worker_profiles WHERE user_id=$1", worker_user_id
    )
    if not worker:
        raise HTTPException(status_code=404, detail="ไม่พบ worker")

    await db.execute(
        "UPDATE worker_profiles SET background_check_status='verified', background_checked_at=NOW() WHERE id=$1",
        worker["id"],
    )
    await db.execute(
        """
        INSERT INTO notifications (user_id, type, title, body)
        VALUES ($1, 'background_check', '✅ ผ่านการตรวจสอบแล้ว',
                'โปรไฟล์ของคุณได้รับ Badge "Verified" แล้ว นายจ้างจะเห็นคุณก่อนคนอื่น')
        """,
        worker_user_id,
    )
    return {"status": "verified"}


@app.patch("/admin/employers/{employer_user_id}/verify", tags=["Admin"])
async def admin_verify_employer(
    employer_user_id: UUID,
    x_admin_secret: str = Header(default=""),
    db: asyncpg.Connection = Depends(get_db),
):
    """Admin อนุมัติ employer verification"""
    if not settings.admin_secret or x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์")

    emp = await db.fetchrow(
        "SELECT id FROM employer_profiles WHERE user_id=$1", employer_user_id
    )
    if not emp:
        raise HTTPException(status_code=404, detail="ไม่พบ employer")

    await db.execute(
        "UPDATE employer_profiles SET verified_status='verified' WHERE id=$1", emp["id"]
    )
    await db.execute(
        """
        INSERT INTO notifications (user_id, type, title, body)
        VALUES ($1, 'employer_verified', '✅ บริษัทได้รับการยืนยันแล้ว',
                'โปรไฟล์ของคุณได้รับ Badge "Verified Employer" แล้ว Worker จะเชื่อถือมากขึ้น')
        """,
        employer_user_id,
    )
    return {"status": "verified"}


# ============================================================
# EMPLOYER VERIFICATION (Mock flow)
# ============================================================

@app.post("/employers/verify/request", tags=["Trust & Safety"])
async def request_employer_verification(
    user: dict = Depends(require_employer),
    db:   asyncpg.Connection = Depends(get_db),
):
    """Employer ส่งคำขอ verify บริษัท — รอ admin อนุมัติ"""
    emp = await db.fetchrow(
        "SELECT id, verified_status FROM employer_profiles WHERE user_id=$1",
        UUID(user["sub"]),
    )
    if not emp:
        raise HTTPException(status_code=404, detail="สร้าง Employer Profile ก่อน")
    if emp["verified_status"] == "verified":
        raise HTTPException(status_code=409, detail="ได้รับการยืนยันแล้ว")
    if emp["verified_status"] == "pending":
        raise HTTPException(status_code=409, detail="รออยู่ระหว่างการตรวจสอบแล้ว")

    await db.execute(
        "UPDATE employer_profiles SET verified_status='pending' WHERE id=$1", emp["id"]
    )
    return {"status": "pending", "message": "ส่งคำขอแล้ว รอ admin อนุมัติ"}


# ============================================================
# REPORT & BLOCK
# ============================================================

class ReportRequest(BaseModel):
    reported_user_id: UUID
    reason:           str = Field(..., pattern="^(spam|fake|harassment|payment_fraud|other)$")
    detail:           Optional[str] = Field(None, max_length=500)

class BlockRequest(BaseModel):
    blocked_user_id: UUID

@app.post("/users/report", status_code=201, tags=["Trust & Safety"])
async def report_user(
    body: ReportRequest,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    reporter_id = UUID(user["sub"])
    if reporter_id == body.reported_user_id:
        raise HTTPException(status_code=400, detail="ไม่สามารถรายงานตัวเองได้")

    # Check ว่า reported user มีอยู่จริง
    exists = await db.fetchval(
        "SELECT id FROM users WHERE id=$1", body.reported_user_id
    )
    if not exists:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")

    # Upsert report (1 คน report 1 คนได้ครั้งเดียว ต่อ reason)
    await db.execute(
        """
        INSERT INTO user_reports (reporter_id, reported_user_id, reason, detail)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (reporter_id, reported_user_id, reason) DO UPDATE
            SET detail     = EXCLUDED.detail,
                updated_at = NOW()
        """,
        reporter_id, body.reported_user_id, body.reason, body.detail,
    )

    # ถ้า report เยอะกว่า 3 ครั้ง จาก user ต่างกัน → auto-flag
    report_count = await db.fetchval(
        """
        SELECT COUNT(DISTINCT reporter_id) FROM user_reports
        WHERE  reported_user_id = $1
        """,
        body.reported_user_id,
    )
    if report_count >= 3:
        logger.warning(f"[trust] user {body.reported_user_id} has {report_count} reports — needs admin review")

    return {"status": "reported", "message": "รายงานถูกส่งแล้ว ทีมงานจะตรวจสอบ"}


@app.post("/users/block", status_code=201, tags=["Trust & Safety"])
async def block_user(
    body: BlockRequest,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    blocker_id = UUID(user["sub"])
    if blocker_id == body.blocked_user_id:
        raise HTTPException(status_code=400, detail="ไม่สามารถบล็อคตัวเองได้")

    await db.execute(
        """
        INSERT INTO user_blocks (blocker_id, blocked_user_id)
        VALUES ($1, $2)
        ON CONFLICT DO NOTHING
        """,
        blocker_id, body.blocked_user_id,
    )
    return {"status": "blocked"}


@app.delete("/users/block/{blocked_user_id}", tags=["Trust & Safety"])
async def unblock_user(
    blocked_user_id: UUID,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    await db.execute(
        "DELETE FROM user_blocks WHERE blocker_id=$1 AND blocked_user_id=$2",
        UUID(user["sub"]), blocked_user_id,
    )
    return {"status": "unblocked"}


@app.get("/users/blocked", tags=["Trust & Safety"])
async def get_blocked_users(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT u.id, u.role, ub.created_at AS blocked_at
        FROM   user_blocks ub
        JOIN   users u ON u.id = ub.blocked_user_id
        WHERE  ub.blocker_id = $1
        ORDER  BY ub.created_at DESC
        """,
        UUID(user["sub"]),
    )
    return [{"user_id": str(r["id"]),
             "role": r["role"], "blocked_at": r["blocked_at"].isoformat()} for r in rows]


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health", tags=["System"])
async def health(db: asyncpg.Connection = Depends(get_db)):
    version = await db.fetchval("SELECT version()")
    return {
        "status":       "ok",
        "db":           "connected",
        "pg":           version.split(" ")[1] if version else "unknown",
        "frontend_url": settings.frontend_url,
        "build":        "2026-05-27-v2",
    }


# ============================================================
# REVIEW SYSTEM
# ============================================================

class ReviewSubmit(BaseModel):
    application_id: UUID
    star_rating:    int       = Field(..., ge=1, le=5)
    tag_keys:       list[str] = Field(default=[])
    would_rehire:   Optional[bool] = None  # employer only

@app.get("/review-tags", tags=["Reviews"])
async def get_review_tags(
    target_role: str,
    db: asyncpg.Connection = Depends(get_db),
):
    if target_role not in ("worker", "employer"):
        raise HTTPException(status_code=400, detail="target_role ต้องเป็น worker หรือ employer")
    rows = await db.fetch(
        "SELECT id, tag_key, tag_label, is_positive FROM review_tags WHERE target_role=$1 ORDER BY sort_order",
        target_role,
    )
    return [dict(r) for r in rows]


@app.post("/reviews", status_code=201, tags=["Reviews"])
async def submit_review(
    body: ReviewSubmit,
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    reviewer_id   = UUID(user["sub"])
    reviewer_role = user["role"]

    app_row = await db.fetchrow(
        """
        SELECT ja.id, ja.worker_id, ja.job_id,
               wp.user_id AS worker_user_id,
               ep.user_id AS employer_user_id
        FROM   job_applications ja
        JOIN   worker_profiles   wp ON wp.id = ja.worker_id
        JOIN   job_postings      jp ON jp.id = ja.job_id
        JOIN   employer_profiles ep ON ep.id = jp.employer_id
        WHERE  ja.id = $1 AND ja.status IN ('hired', 'verified', 'disputed')
        """,
        body.application_id,
    )
    if not app_row:
        raise HTTPException(status_code=404, detail="ไม่พบงานที่ได้รับการจ้าง")

    if reviewer_role == "worker" and app_row["worker_user_id"] != reviewer_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ review งานนี้")
    if reviewer_role == "employer" and app_row["employer_user_id"] != reviewer_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ review งานนี้")

    reviewee_id  = app_row["employer_user_id"] if reviewer_role == "worker" else app_row["worker_user_id"]
    would_rehire = body.would_rehire if reviewer_role == "employer" else None

    try:
        review = await db.fetchrow(
            """
            INSERT INTO reviews
                (application_id, reviewer_id, reviewee_id, reviewer_role, star_rating, would_rehire)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
            """,
            body.application_id, reviewer_id, reviewee_id,
            reviewer_role, body.star_rating, would_rehire,
        )
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="คุณ review งานนี้ไปแล้ว")

    if body.tag_keys:
        tag_rows = await db.fetch(
            "SELECT id FROM review_tags WHERE tag_key = ANY($1::text[])", body.tag_keys,
        )
        if tag_rows:
            await db.executemany(
                "INSERT INTO review_tag_selections (review_id, tag_id) VALUES ($1, $2)",
                [(review["id"], r["id"]) for r in tag_rows],
            )

    # Auto-reveal ถ้าทั้งคู่ส่งแล้ว
    count = await db.fetchval(
        "SELECT COUNT(*) FROM reviews WHERE application_id=$1", body.application_id,
    )
    if count >= 2:
        await db.execute(
            "UPDATE reviews SET is_visible=TRUE, revealed_at=NOW() WHERE application_id=$1 AND is_visible=FALSE",
            body.application_id,
        )

    return {"review_id": str(review["id"]), "status": "submitted"}


@app.get("/reviews/me", tags=["Reviews"])
async def get_my_reviews(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """
        SELECT r.id, r.star_rating, r.would_rehire, r.reviewer_role,
               r.revealed_at, jp.title AS job_title,
               ARRAY_AGG(rt.tag_label ORDER BY rt.sort_order)
                   FILTER (WHERE rt.id IS NOT NULL) AS tags
        FROM   reviews r
        JOIN   job_applications ja ON ja.id = r.application_id
        JOIN   job_postings     jp ON jp.id = ja.job_id
        LEFT JOIN review_tag_selections rts ON rts.review_id = r.id
        LEFT JOIN review_tags           rt  ON rt.id = rts.tag_id
        WHERE  r.reviewee_id = $1 AND r.is_visible = TRUE
        GROUP  BY r.id, jp.title
        ORDER  BY r.revealed_at DESC
        """,
        UUID(user["sub"]),
    )
    return [
        {
            "review_id":     str(r["id"]),
            "star_rating":   r["star_rating"],
            "would_rehire":  r["would_rehire"],
            "reviewer_role": r["reviewer_role"],
            "job_title":     r["job_title"],
            "tags":          r["tags"] or [],
            "revealed_at":   r["revealed_at"].isoformat() if r["revealed_at"] else None,
        }
        for r in rows
    ]


@app.get("/reviews/pending", tags=["Reviews"])
async def get_pending_reviews(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    user_id = UUID(user["sub"])
    role    = user["role"]

    if role == "worker":
        rows = await db.fetch(
            """
            SELECT ja.id AS application_id, jp.title AS job_title,
                   ep.company_name, ja.decided_at
            FROM   job_applications ja
            JOIN   job_postings      jp ON jp.id = ja.job_id
            JOIN   employer_profiles ep ON ep.id = jp.employer_id
            JOIN   worker_profiles   wp ON wp.id = ja.worker_id
            WHERE  wp.user_id = $1 AND ja.status = 'hired'
              AND  NOT EXISTS (
                  SELECT 1 FROM reviews r
                  WHERE  r.application_id = ja.id AND r.reviewer_id = $1
              )
            ORDER BY ja.decided_at DESC
            """,
            user_id,
        )
        return [{"application_id": str(r["application_id"]), "job_title": r["job_title"],
                 "company_name": r["company_name"], "review_target": "employer",
                 "decided_at": r["decided_at"].isoformat() if r["decided_at"] else None}
                for r in rows]
    else:
        rows = await db.fetch(
            """
            SELECT ja.id AS application_id, jp.title AS job_title,
                   wp.full_name AS worker_name, ja.decided_at
            FROM   job_applications ja
            JOIN   job_postings      jp ON jp.id = ja.job_id
            JOIN   employer_profiles ep ON ep.id = jp.employer_id
            JOIN   worker_profiles   wp ON wp.id = ja.worker_id
            WHERE  ep.user_id = $1 AND ja.status = 'hired'
              AND  NOT EXISTS (
                  SELECT 1 FROM reviews r
                  WHERE  r.application_id = ja.id AND r.reviewer_id = $1
              )
            ORDER BY ja.decided_at DESC
            """,
            user_id,
        )
        return [{"application_id": str(r["application_id"]), "job_title": r["job_title"],
                 "worker_name": r["worker_name"], "review_target": "worker",
                 "decided_at": r["decided_at"].isoformat() if r["decided_at"] else None}
                for r in rows]

# ─────────────────────────────────────────────
#  DELETE ACCOUNT
# ─────────────────────────────────────────────
@app.delete("/users/me", tags=["Auth"])
async def delete_my_account(
    user: dict = Depends(get_current_user),
    db:   asyncpg.Connection = Depends(get_db),
):
    """
    Soft-delete: sets is_active=False + deletion_requested_at=NOW()
    Blocks if user has active hired/working jobs.
    Hard delete happens 7 days later via cron (not yet implemented).
    """
    user_id = UUID(user["sub"])
    role    = user["role"]

    # ❌ บล็อกถ้ามีงานที่ยังค้างอยู่
    if role == "worker":
        active_job = await db.fetchval(
            """
            SELECT ja.id FROM job_applications ja
            JOIN   worker_profiles wp ON wp.id = ja.worker_id
            WHERE  wp.user_id = $1
              AND  ja.status IN ('hired','checked_in','working')
            LIMIT 1
            """,
            user_id,
        )
    else:
        active_job = await db.fetchval(
            """
            SELECT jp.id FROM job_postings jp
            JOIN   employer_profiles ep ON ep.id = jp.employer_id
            WHERE  ep.user_id = $1
              AND  jp.status = 'open'
              AND  jp.slots_filled > 0
            LIMIT 1
            """,
            user_id,
        )

    if active_job:
        raise HTTPException(
            status_code=400,
            detail="ไม่สามารถลบบัญชีได้ขณะมีงานที่ยังดำเนินอยู่ กรุณาสิ้นสุดงานทั้งหมดก่อน"
        )

    # ✅ Soft delete
    await db.execute(
        """
        UPDATE users
        SET    is_active = FALSE,
               deletion_requested_at = NOW()
        WHERE  id = $1
        """,
        user_id,
    )

    return {
        "message": "บัญชีของคุณถูกระงับแล้ว ข้อมูลทั้งหมดจะถูกลบถาวรภายใน 7 วัน"
    }
