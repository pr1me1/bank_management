import click
from sqlalchemy.orm import Session

from app.admin import AdminUser
from app.db import SessionLocal
from app.utils import hash_password


@click.group()
def cli():
    """FastAPI Management Commands"""
    pass


@cli.command()
@click.option('--email', prompt='Email', help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
def create_admin(email: str, password: str):
    db: Session = SessionLocal()

    existing = db.query(AdminUser).filter(AdminUser.email == email).first()
    if existing:
        click.echo(click.style(f"❌ Admin '{email}' allaqachon mavjud!", fg='red'))
        return

    try:
        admin = AdminUser(
            email=email,
            password_hash=hash_password(password),
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        click.echo(click.style(f"✅ Admin '{email}' muvaffaqiyatli yaratildi!", fg='green'))
    except Exception as e:
        db.rollback()
        click.echo(click.style(f"❌ Xato: {str(e)}", fg='red'))
    finally:
        db.close()


if __name__ == '__main__':
    cli()
