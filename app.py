from contextlib import asynccontextmanager, closing
from pathlib import Path
import sqlite3
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "employees.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    address TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    salary REAL NOT NULL,
                    department TEXT NOT NULL
                )
                """
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


NameForm = Annotated[str, Form(...)]
GenderForm = Annotated[str, Form(...)]
AddressForm = Annotated[str, Form(...)]
PhoneForm = Annotated[str, Form(...)]
SalaryForm = Annotated[float, Form(...)]
DepartmentForm = Annotated[str, Form(...)]


@app.get("/")
async def index(request: Request):
    with closing(get_connection()) as connection:
        employees = connection.execute(
            "SELECT * FROM employees ORDER BY id DESC"
        ).fetchall()

    return templates.TemplateResponse(
        request,
        "index.html",
        {"employees": employees, "error": ""},
    )


@app.get("/add")
async def add_employee_form(request: Request):
    return templates.TemplateResponse(request, "add.html")


@app.post("/add")
async def add_employee(
    name: NameForm,
    gender: GenderForm,
    address: AddressForm,
    phone: PhoneForm,
    salary: SalaryForm,
    department: DepartmentForm,
):
    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                """
                INSERT INTO employees (name, gender, address, phone, salary, department)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, gender, address, phone, salary, department),
            )

    return RedirectResponse("/", status_code=303)


@app.get("/edit/{employee_id}")
async def edit_employee_form(request: Request, employee_id: int):
    with closing(get_connection()) as connection:
        employee = connection.execute(
            "SELECT * FROM employees WHERE id = ?", (employee_id,)
        ).fetchone()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return templates.TemplateResponse(
        request,
        "edit.html",
        {"employee": employee},
    )


@app.post("/edit/{employee_id}")
async def edit_employee(
    employee_id: int,
    name: NameForm,
    gender: GenderForm,
    address: AddressForm,
    phone: PhoneForm,
    salary: SalaryForm,
    department: DepartmentForm,
):
    with closing(get_connection()) as connection:
        with connection:
            result = connection.execute(
                """
                UPDATE employees
                SET name = ?, gender = ?, address = ?, phone = ?, salary = ?, department = ?
                WHERE id = ?
                """,
                (name, gender, address, phone, salary, department, employee_id),
            )

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    return RedirectResponse("/", status_code=303)


@app.post("/delete")
async def delete_employee(emp_id: Annotated[int, Form(...)]):
    with closing(get_connection()) as connection:
        with connection:
            connection.execute("DELETE FROM employees WHERE id = ?", (emp_id,))

    return RedirectResponse("/", status_code=303)
