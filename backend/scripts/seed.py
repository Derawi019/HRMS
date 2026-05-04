#!/usr/bin/env python3
"""Load demo roster into Postgres after migrations. Run from `backend/`:
   DATABASE_URL=... python scripts/seed.py

Runs only when the employees table is empty. To add the extra departments + 20 people
without wiping existing rows, use `scripts/seed_expansion.py` instead.
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    ChatMessage,
    Department,
    Employee,
    EmployeeCredential,
    LeaveRequest,
    LeaveStatus,
    Notification,
    Role,
    Task,
    TaskStatus,
)
from app.security import hash_password  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        if db.query(Employee).first():
            print("employees already seeded — skipping")
            return

        dept_rows = [
            ("Executive", "EXE"),
            ("Engineering", "ENG"),
            ("Product", "PRD"),
            ("Finance", "FIN"),
            ("Human Resources", "HR"),
            ("Support", "SUP"),
            ("Marketing", "MKT"),
            ("Legal", "LGL"),
            ("Sales", "SLS"),
            ("Research", "RND"),
            ("Operations", "OPS"),
            ("Design", "DSN"),
        ]
        dept_id: dict[str, int] = {}
        for name, code in dept_rows:
            d = Department(name=name, code=code, is_active=True)
            db.add(d)
            db.flush()
            dept_id[name] = d.id

        def add_cred(employee_id: int, raw_pw: str) -> None:
            db.add(EmployeeCredential(employee_id=employee_id, password_hash=hash_password(raw_pw)))

        def add_employee(
            *,
            first: str,
            last: str,
            email: str,
            phone: str,
            role: Role,
            title: str,
            salary: float,
            started: date,
            manager_id: int | None,
            dept_name: str,
            password: str,
            dob: date | None = None,
            rating: float = 4,
            goals_completed: str = "4 / 10",
            peer_reviews: int = 2,
            attendance: dict | None = None,
            leave_balance: dict | None = None,
            gender: str = "Other",
            nationality: str = "United States",
            marital: str = "Single",
            address: str = "Remote",
            emergency: str = "—",
        ) -> Employee:
            initials = (first[:1] + last[:1]).upper()
            e = Employee(
                first=first,
                last=last,
                initials=initials,
                email=email,
                phone=phone,
                role=role,
                title=title,
                salary=float(salary),
                status="active",
                start=started,
                manager_id=manager_id,
                department_id=dept_id[dept_name],
                dob=dob,
                gender=gender,
                nationality=nationality,
                marital=marital,
                address=address,
                emergency=emergency,
                rating=rating,
                goals_completed=goals_completed,
                peer_reviews=peer_reviews,
                attendance=attendance or {"present": 200, "late": 4, "absent": 1, "avgHrs": "8.2"},
                leave_balance=leave_balance or {"annual": "14 / 20", "sick": "8 / 10", "personal": "3 / 5"},
            )
            db.add(e)
            db.flush()
            add_cred(e.id, password)
            return e

        admin = add_employee(
            first="John",
            last="Doe",
            email="john.doe@company.com",
            phone="+1 (555) 100-2042",
            role=Role.admin,
            title="Chief People Officer",
            salary=195000,
            started=date(2018, 1, 15),
            manager_id=None,
            dept_name="Executive",
            password="admin@123",
            dob=date(1982, 6, 3),
            rating=5,
            goals_completed="9 / 10",
            attendance={"present": 248, "late": 3, "absent": 0, "avgHrs": "9.2"},
        )
        rita = add_employee(
            first="Rita",
            last="Gomez",
            email="rita.gomez@company.com",
            phone="+1 (555) 111-9821",
            role=Role.manager,
            title="Engineering Manager",
            salary=135000,
            started=date(2019, 4, 8),
            manager_id=admin.id,
            dept_name="Engineering",
            password="rita@123",
            dob=date(1987, 9, 21),
            peer_reviews=4,
            attendance={"present": 230, "late": 4, "absent": 1, "avgHrs": "8.5"},
        )
        tanya = add_employee(
            first="Tanya",
            last="Johnson",
            email="tanya.johnson@company.com",
            phone="+1 (555) 902-7741",
            role=Role.manager,
            title="Product Manager",
            salary=128000,
            started=date(2020, 2, 3),
            manager_id=admin.id,
            dept_name="Product",
            password="tanya@123",
            dob=date(1991, 2, 17),
            peer_reviews=3,
            attendance={"present": 226, "late": 5, "absent": 1, "avgHrs": "8.3"},
        )

        liam = add_employee(
            first="Liam",
            last="Watkins",
            email="liam.watkins@company.com",
            phone="+1 (555) 442-8890",
            role=Role.employee,
            title="Frontend Engineer",
            salary=112000,
            started=date(2021, 6, 1),
            manager_id=rita.id,
            dept_name="Engineering",
            password="liam@123",
            address="Austin, TX",
            attendance={"present": 218, "late": 6, "absent": 2, "avgHrs": "8.1"},
        )
        priya = add_employee(
            first="Priya",
            last="Sharma",
            email="priya.sharma@company.com",
            phone="+1 (555) 221-7740",
            role=Role.employee,
            title="Backend Engineer",
            salary=118000,
            started=date(2021, 3, 22),
            manager_id=rita.id,
            dept_name="Engineering",
            password="priya@123",
            goals_completed="6 / 10",
            attendance={"present": 222, "late": 3, "absent": 1, "avgHrs": "8.4"},
        )
        jamal = add_employee(
            first="Jamal",
            last="Mitchell",
            email="jamal.mitchell@company.com",
            phone="+1 (555) 603-9912",
            role=Role.employee,
            title="QA Analyst",
            salary=89000,
            started=date(2022, 7, 5),
            manager_id=rita.id,
            dept_name="Engineering",
            password="jamal@123",
            goals_completed="3 / 10",
            attendance={"present": 198, "late": 8, "absent": 2, "avgHrs": "7.9"},
        )
        ethan = add_employee(
            first="Ethan",
            last="Kim",
            email="ethan.kim@company.com",
            phone="+1 (555) 884-6612",
            role=Role.employee,
            title="DevOps Engineer",
            salary=122000,
            started=date(2020, 9, 9),
            manager_id=rita.id,
            dept_name="Engineering",
            password="ethan@123",
            goals_completed="7 / 10",
            attendance={"present": 234, "late": 2, "absent": 0, "avgHrs": "8.5"},
        )

        sofia = add_employee(
            first="Sofia",
            last="Reyes",
            email="sofia.reyes@company.com",
            phone="+1 (555) 441-6610",
            role=Role.employee,
            title="Product Designer",
            salary=102000,
            started=date(2021, 9, 1),
            manager_id=tanya.id,
            dept_name="Product",
            password="sofia@123",
            attendance={"present": 214, "late": 4, "absent": 1, "avgHrs": "8.0"},
        )
        maya = add_employee(
            first="Maya",
            last="Chen",
            email="maya.chen@company.com",
            phone="+1 (555) 778-5541",
            role=Role.employee,
            title="Product Analyst",
            salary=96000,
            started=date(2022, 3, 7),
            manager_id=tanya.id,
            dept_name="Product",
            password="maya@123",
            attendance={"present": 206, "late": 5, "absent": 2, "avgHrs": "7.8"},
        )
        akash = add_employee(
            first="Akash",
            last="Verma",
            email="akash.verma@company.com",
            phone="+1 (555) 229-8842",
            role=Role.employee,
            title="Data Analyst",
            salary=105000,
            started=date(2023, 1, 16),
            manager_id=tanya.id,
            dept_name="Product",
            password="akash@123",
            rating=3,
            goals_completed="2 / 10",
            attendance={"present": 188, "late": 4, "absent": 1, "avgHrs": "8.0"},
        )
        _ = add_employee(
            first="Nora",
            last="Okafor",
            email="nora.okafor@company.com",
            phone="+1 (555) 339-7743",
            role=Role.employee,
            title="Product Marketing",
            salary=99000,
            started=date(2022, 9, 6),
            manager_id=tanya.id,
            dept_name="Product",
            password="nora@123",
            attendance={"present": 202, "late": 3, "absent": 2, "avgHrs": "8.2"},
        )

        # --- Expanded roster: 9 managers + 11 ICs across all departments (20 new accounts) ---
        def pw(first: str, last: str) -> str:
            return f"{first.lower()}.{last.lower()}@123"

        mgr_finance = add_employee(
            first="Marcus",
            last="Hale",
            email="marcus.hale@company.com",
            phone="+1 (555) 401-1101",
            role=Role.manager,
            title="Finance Manager",
            salary=142000,
            started=date(2019, 5, 13),
            manager_id=admin.id,
            dept_name="Finance",
            password=pw("Marcus", "Hale"),
            dob=date(1985, 4, 22),
            attendance={"present": 236, "late": 2, "absent": 0, "avgHrs": "8.4"},
        )
        mgr_hr = add_employee(
            first="Elena",
            last="Park",
            email="elena.park@company.com",
            phone="+1 (555) 401-1102",
            role=Role.manager,
            title="HR Manager",
            salary=138000,
            started=date(2019, 8, 19),
            manager_id=admin.id,
            dept_name="Human Resources",
            password=pw("Elena", "Park"),
            dob=date(1988, 11, 8),
            peer_reviews=5,
            attendance={"present": 228, "late": 3, "absent": 1, "avgHrs": "8.3"},
        )
        mgr_support = add_employee(
            first="Omar",
            last="Farouk",
            email="omar.farouk@company.com",
            phone="+1 (555) 401-1103",
            role=Role.manager,
            title="Support Manager",
            salary=125000,
            started=date(2020, 1, 6),
            manager_id=admin.id,
            dept_name="Support",
            password=pw("Omar", "Farouk"),
            dob=date(1990, 3, 14),
            attendance={"present": 220, "late": 4, "absent": 2, "avgHrs": "8.1"},
        )
        mgr_marketing = add_employee(
            first="Nina",
            last="Brooks",
            email="nina.brooks@company.com",
            phone="+1 (555) 401-1104",
            role=Role.manager,
            title="Marketing Manager",
            salary=131000,
            started=date(2020, 6, 15),
            manager_id=admin.id,
            dept_name="Marketing",
            password=pw("Nina", "Brooks"),
            dob=date(1989, 7, 29),
            attendance={"present": 224, "late": 3, "absent": 1, "avgHrs": "8.2"},
        )
        mgr_legal = add_employee(
            first="Derek",
            last="Vaughn",
            email="derek.vaughn@company.com",
            phone="+1 (555) 401-1105",
            role=Role.manager,
            title="Legal Lead",
            salary=148000,
            started=date(2018, 11, 5),
            manager_id=admin.id,
            dept_name="Legal",
            password=pw("Derek", "Vaughn"),
            dob=date(1983, 2, 11),
            attendance={"present": 232, "late": 2, "absent": 0, "avgHrs": "8.6"},
        )
        mgr_sales = add_employee(
            first="Sierra",
            last="Blake",
            email="sierra.blake@company.com",
            phone="+1 (555) 401-1106",
            role=Role.manager,
            title="Sales Director",
            salary=152000,
            started=date(2019, 2, 25),
            manager_id=admin.id,
            dept_name="Sales",
            password=pw("Sierra", "Blake"),
            dob=date(1986, 9, 3),
            attendance={"present": 218, "late": 5, "absent": 1, "avgHrs": "8.5"},
        )
        mgr_research = add_employee(
            first="Yuki",
            last="Tanaka",
            email="yuki.tanaka@company.com",
            phone="+1 (555) 401-1107",
            role=Role.manager,
            title="Research Lead",
            salary=149000,
            started=date(2020, 4, 20),
            manager_id=admin.id,
            dept_name="Research",
            password=pw("Yuki", "Tanaka"),
            dob=date(1987, 12, 19),
            goals_completed="8 / 10",
            attendance={"present": 226, "late": 2, "absent": 1, "avgHrs": "8.4"},
        )
        mgr_operations = add_employee(
            first="Carlos",
            last="Mendez",
            email="carlos.mendez@company.com",
            phone="+1 (555) 401-1108",
            role=Role.manager,
            title="Operations Manager",
            salary=134000,
            started=date(2021, 3, 1),
            manager_id=admin.id,
            dept_name="Operations",
            password=pw("Carlos", "Mendez"),
            dob=date(1992, 5, 7),
            attendance={"present": 214, "late": 4, "absent": 2, "avgHrs": "8.0"},
        )
        mgr_design = add_employee(
            first="Hannah",
            last="Irving",
            email="hannah.irving@company.com",
            phone="+1 (555) 401-1109",
            role=Role.manager,
            title="Design Lead",
            salary=136000,
            started=date(2021, 8, 16),
            manager_id=admin.id,
            dept_name="Design",
            password=pw("Hannah", "Irving"),
            dob=date(1991, 1, 26),
            attendance={"present": 210, "late": 3, "absent": 1, "avgHrs": "8.1"},
        )

        add_employee(
            first="Aiden",
            last="Frost",
            email="aiden.frost@company.com",
            phone="+1 (555) 402-2201",
            role=Role.employee,
            title="Staff Engineer",
            salary=124000,
            started=date(2022, 4, 11),
            manager_id=rita.id,
            dept_name="Engineering",
            password=pw("Aiden", "Frost"),
            goals_completed="7 / 10",
            attendance={"present": 216, "late": 4, "absent": 1, "avgHrs": "8.3"},
        )
        add_employee(
            first="Zoe",
            last="Patel",
            email="zoe.patel@company.com",
            phone="+1 (555) 402-2202",
            role=Role.employee,
            title="Mobile Engineer",
            salary=116000,
            started=date(2023, 2, 27),
            manager_id=rita.id,
            dept_name="Engineering",
            password=pw("Zoe", "Patel"),
            attendance={"present": 198, "late": 5, "absent": 2, "avgHrs": "8.0"},
        )
        add_employee(
            first="Finn",
            last="Doyle",
            email="finn.doyle@company.com",
            phone="+1 (555) 402-2203",
            role=Role.employee,
            title="Product Owner",
            salary=118000,
            started=date(2022, 8, 8),
            manager_id=tanya.id,
            dept_name="Product",
            password=pw("Finn", "Doyle"),
            attendance={"present": 208, "late": 4, "absent": 1, "avgHrs": "8.2"},
        )
        add_employee(
            first="Ivy",
            last="Santos",
            email="ivy.santos@company.com",
            phone="+1 (555) 402-2204",
            role=Role.employee,
            title="Program Manager",
            salary=114000,
            started=date(2023, 6, 12),
            manager_id=tanya.id,
            dept_name="Product",
            password=pw("Ivy", "Santos"),
            attendance={"present": 192, "late": 6, "absent": 2, "avgHrs": "7.9"},
        )
        add_employee(
            first="Walter",
            last="Cho",
            email="walter.cho@company.com",
            phone="+1 (555) 402-2205",
            role=Role.employee,
            title="Financial Analyst",
            salary=92000,
            started=date(2021, 10, 4),
            manager_id=mgr_finance.id,
            dept_name="Finance",
            password=pw("Walter", "Cho"),
            attendance={"present": 222, "late": 3, "absent": 1, "avgHrs": "8.2"},
        )
        add_employee(
            first="Greta",
            last="Lind",
            email="greta.lind@company.com",
            phone="+1 (555) 402-2206",
            role=Role.employee,
            title="HR Specialist",
            salary=78000,
            started=date(2022, 1, 17),
            manager_id=mgr_hr.id,
            dept_name="Human Resources",
            password=pw("Greta", "Lind"),
            attendance={"present": 218, "late": 3, "absent": 2, "avgHrs": "8.1"},
        )
        add_employee(
            first="Rex",
            last="Nolan",
            email="rex.nolan@company.com",
            phone="+1 (555) 402-2207",
            role=Role.employee,
            title="Support Engineer",
            salary=88000,
            started=date(2023, 3, 20),
            manager_id=mgr_support.id,
            dept_name="Support",
            password=pw("Rex", "Nolan"),
            attendance={"present": 204, "late": 5, "absent": 3, "avgHrs": "7.9"},
        )
        add_employee(
            first="Jade",
            last="Porter",
            email="jade.porter@company.com",
            phone="+1 (555) 402-2208",
            role=Role.employee,
            title="Growth Marketer",
            salary=102000,
            started=date(2022, 5, 9),
            manager_id=mgr_marketing.id,
            dept_name="Marketing",
            password=pw("Jade", "Porter"),
            attendance={"present": 212, "late": 4, "absent": 2, "avgHrs": "8.0"},
        )
        add_employee(
            first="Beau",
            last="Sterling",
            email="beau.sterling@company.com",
            phone="+1 (555) 402-2209",
            role=Role.employee,
            title="Paralegal",
            salary=87000,
            started=date(2023, 9, 5),
            manager_id=mgr_legal.id,
            dept_name="Legal",
            password=pw("Beau", "Sterling"),
            attendance={"present": 196, "late": 4, "absent": 1, "avgHrs": "8.0"},
        )
        add_employee(
            first="Tucker",
            last="Wade",
            email="tucker.wade@company.com",
            phone="+1 (555) 402-2210",
            role=Role.employee,
            title="Account Executive",
            salary=98000,
            started=date(2022, 11, 14),
            manager_id=mgr_sales.id,
            dept_name="Sales",
            password=pw("Tucker", "Wade"),
            attendance={"present": 206, "late": 6, "absent": 2, "avgHrs": "8.3"},
        )
        add_employee(
            first="Ada",
            last="Mueller",
            email="ada.mueller@company.com",
            phone="+1 (555) 402-2211",
            role=Role.employee,
            title="Research Scientist",
            salary=132000,
            started=date(2021, 7, 6),
            manager_id=mgr_research.id,
            dept_name="Research",
            password=pw("Ada", "Mueller"),
            goals_completed="6 / 10",
            attendance={"present": 224, "late": 2, "absent": 0, "avgHrs": "8.5"},
        )
        add_employee(
            first="Quinn",
            last="Reeves",
            email="quinn.reeves@company.com",
            phone="+1 (555) 402-2212",
            role=Role.employee,
            title="Ops Coordinator",
            salary=76000,
            started=date(2023, 4, 24),
            manager_id=mgr_operations.id,
            dept_name="Operations",
            password=pw("Quinn", "Reeves"),
            attendance={"present": 188, "late": 5, "absent": 2, "avgHrs": "7.8"},
        )
        add_employee(
            first="Miles",
            last="Orchard",
            email="miles.orchard@company.com",
            phone="+1 (555) 402-2213",
            role=Role.employee,
            title="Product Designer",
            salary=108000,
            started=date(2022, 2, 28),
            manager_id=mgr_design.id,
            dept_name="Design",
            password=pw("Miles", "Orchard"),
            attendance={"present": 214, "late": 3, "absent": 1, "avgHrs": "8.2"},
        )

        db.add_all(
            [
                LeaveRequest(
                    employee_id=maya.id,
                    type="Paid Leave",
                    start_date=date(2026, 3, 24),
                    end_date=date(2026, 3, 26),
                    reason="Family commitment",
                    status=LeaveStatus.pending,
                ),
                LeaveRequest(
                    employee_id=priya.id,
                    type="Sick Leave",
                    start_date=date(2026, 2, 26),
                    end_date=date(2026, 2, 27),
                    reason="Flu symptoms",
                    status=LeaveStatus.pending,
                ),
                LeaveRequest(
                    employee_id=liam.id,
                    type="Personal Leave",
                    start_date=date(2026, 3, 6),
                    end_date=date(2026, 3, 6),
                    reason="",
                    status=LeaveStatus.approved,
                ),
                LeaveRequest(
                    employee_id=sofia.id,
                    type="Paid Leave",
                    start_date=date(2026, 3, 6),
                    end_date=date(2026, 3, 9),
                    reason="",
                    status=LeaveStatus.approved,
                ),
                LeaveRequest(
                    employee_id=ethan.id,
                    type="Sick Leave",
                    start_date=date(2026, 7, 6),
                    end_date=date(2026, 7, 8),
                    reason="",
                    status=LeaveStatus.approved,
                ),
                LeaveRequest(
                    employee_id=akash.id,
                    type="Paid Leave",
                    start_date=date(2026, 6, 6),
                    end_date=date(2026, 6, 7),
                    reason="Holiday overlap",
                    status=LeaveStatus.rejected,
                ),
            ]
        )

        db.add_all(
            [
                Task(
                    title="Update engineering policy handbook",
                    assignee_id=liam.id,
                    due="Feb 28",
                    status=TaskStatus.inprogress,
                    priority="high",
                ),
                Task(
                    title="QA regression run for onboarding",
                    assignee_id=jamal.id,
                    due="Mar 3",
                    status=TaskStatus.todo,
                    priority="medium",
                ),
                Task(
                    title="Product analytics dashboard review",
                    assignee_id=akash.id,
                    due="Feb 29",
                    status=TaskStatus.todo,
                    priority="medium",
                ),
                Task(
                    title="Design review: mobile approvals",
                    assignee_id=sofia.id,
                    due="Mar 14",
                    status=TaskStatus.inprogress,
                    priority="medium",
                ),
                Task(
                    title="Launch HRMS rollout email",
                    assignee_id=rita.id,
                    due=None,
                    status=TaskStatus.done,
                    priority=None,
                ),
                Task(
                    title="Backup payroll exports",
                    assignee_id=admin.id,
                    due=None,
                    status=TaskStatus.done,
                    priority=None,
                ),
            ]
        )

        db.add_all(
            [
                ChatMessage(sender_id=rita.id, body="Team reminder: sprint planning @ 11am tomorrow."),
                ChatMessage(sender_id=liam.id, body="Attendance export is ready — link in Slack."),
                ChatMessage(sender_id=maya.id, body="Can someone approve my leave overlap with design review?"),
            ]
        )

        db.add_all(
            [
                Notification(
                    target_id=admin.id,
                    type="system",
                    dot="purple",
                    title="Quarterly Compliance",
                    text="3 employees have training due this week.",
                    read=False,
                ),
                Notification(
                    target_id=maya.id,
                    type="task",
                    dot="orange",
                    title="Action needed",
                    text="Please confirm payroll settings by Friday.",
                    read=False,
                ),
            ]
        )

        db.commit()
        print("seed complete:", os.getenv("DATABASE_URL", "").split("@")[-1])
    finally:
        db.close()


if __name__ == "__main__":
    main()
