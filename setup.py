import uuid
import typer
from typing import Annotated, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from click import Choice
from settings import (
    Settings,
    DBSettings,
    AppConfig,
    LocalStoreSettings,
    GCloudStoreSettings,
    DBType,
    DatastoreType,
    LogLevel,
    StorageSettings,
)

app = typer.Typer()
settings = Settings()
console = Console()


def create_table(title, data):
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="dim")
    table.add_column("Value")
    for key, value in data.items():
        table.add_row(key, str(value))
    return table


@app.command()
def setup_db(
    db_type: Annotated[
        Optional[DBType],
        typer.Option(help="Database type: 'sql' or 'mongodb'", case_sensitive=False),
    ] = settings.db.db_type,
    pool_size: Annotated[
        Optional[int],
        typer.Option(help="Database connection pool size"),
    ] = settings.db.pool_size,
    max_overflow: Annotated[
        Optional[int],
        typer.Option(help="Maximum number of connections beyond pool_size"),
    ] = settings.db.max_overflow,
    interactive: Annotated[
        bool,
        typer.Option("--interactive", "-i", help="Use interactive prompts"),
    ] = False,
):
    """Setup database settings."""
    if interactive:
        db_type = typer.prompt(
            "Database type",
            default=db_type,
            type=Choice([e.value for e in DBType]),
            show_default=True,
        )
        pool_size = typer.prompt(
            "Connection pool size",
            default=settings.db.pool_size,
            type=int,
            show_default=True,
        )
        max_overflow = typer.prompt(
            "Max overflow",
            default=settings.db.max_overflow,
            type=int,
            show_default=True,
        )

    settings.db = DBSettings(
        db_type=DBType(db_type), pool_size=pool_size, max_overflow=max_overflow
    )
    settings.save()
    console.print(create_table("Database Settings", settings.db.dict()))


@app.command()
def setup_storage(
    datastore: Annotated[
        Optional[DatastoreType],
        typer.Option(help="Datastore type: 'local' or 'gcloud'", case_sensitive=False),
    ] = settings.storage.datastore,
    base_path: Annotated[
        Optional[Path],
        typer.Option(help="Local base path (for local datastore)"),
    ] = Path(settings.storage.local.base_path),
    bucket_name: Annotated[
        Optional[str],
        typer.Option(
            help="GCloud bucket name (for gcloud datastore)",
            envvar="GCLOUD_BUCKET_NAME",
        ),
    ] = settings.storage.gcloud.bucket_name,
    project_id: Annotated[
        Optional[str],
        typer.Option(
            help="GCloud project ID (for gcloud datastore)",
            envvar="GCLOUD_PROJECT_ID",
        ),
    ] = settings.storage.gcloud.project_id,
    interactive: Annotated[
        bool,
        typer.Option("--interactive", "-i", help="Use interactive prompts"),
    ] = False,
):
    """Setup storage settings."""
    if interactive:
        datastore = typer.prompt(
            "Datastore type",
            default=datastore,
            type=Choice([e.value for e in DatastoreType]),
            show_default=True,
        )
        if datastore == DatastoreType.LOCAL.value:
            base_path = typer.prompt(
                "Local base path",
                default=settings.storage.local.base_path,
                type=str,
                show_default=True,
            )
            base_path = Path(base_path).resolve()
            if not base_path.exists():
                create_dir = typer.confirm(f"Directory {base_path} does not exist. Create it?")
                if create_dir:
                    base_path.mkdir(parents=True, exist_ok=True)
                else:
                    typer.echo("Aborting setup.")
                    raise typer.Abort()
            elif any(base_path.iterdir()):
                import uuid

                def is_valid_uuid(value):
                    try:
                        uuid.UUID(str(value))
                        return True
                    except ValueError:
                        return False

                is_valid = all(
                    folder.is_dir()
                    and is_valid_uuid(folder.name)
                    and all(is_valid_uuid(file.stem) for file in folder.iterdir() if file.is_file())
                    for folder in base_path.iterdir()
                    if folder.is_dir()
                )
                if not is_valid:
                    typer.echo(f"Directory {base_path} contains invalid content. Aborting setup.")
                    raise typer.Abort()
            local_settings = LocalStoreSettings(base_path=str(base_path))
            gcloud_settings = settings.storage.gcloud
        elif datastore == DatastoreType.GCLOUD.value:
            bucket_name = typer.prompt(
                "GCloud bucket name",
                default=settings.storage.gcloud.bucket_name,
                type=str,
                show_default=True,
            )
            project_id = typer.prompt(
                "GCloud project ID",
                default=settings.storage.gcloud.project_id,
                type=str,
                show_default=True,
            )
            gcloud_settings = GCloudStoreSettings(bucket_name=bucket_name, project_id=project_id)
            local_settings = settings.storage.local
    else:
        local_settings = LocalStoreSettings(base_path=str(base_path))
        gcloud_settings = GCloudStoreSettings(bucket_name=bucket_name, project_id=project_id)

    settings.storage = StorageSettings(
        datastore=DatastoreType(datastore),
        local=local_settings,
        gcloud=gcloud_settings,
    )
    settings.save()
    console.print(create_table("Storage Settings", settings.storage.dict()))


@app.command()
def setup_app(
    debug: Annotated[Optional[bool], typer.Option(help="Enable debug mode")] = settings.app.debug,
    log_level: Annotated[
        Optional[LogLevel],
        typer.Option(
            help="Log level: DEBUG, INFO, WARNING, ERROR, or CRITICAL",
            case_sensitive=False,
        ),
    ] = settings.app.log_level,
    interactive: Annotated[
        bool,
        typer.Option("--interactive", "-i", help="Use interactive prompts"),
    ] = False,
):
    """Setup application settings."""
    if interactive:
        debug = typer.confirm("Debug mode", default=debug)
        log_level = typer.prompt(
            "Log level",
            default=log_level,
            type=Choice([e.value for e in LogLevel]),
            show_default=True,
        )

    settings.app = AppConfig(
        debug=debug,
        log_level=LogLevel(log_level),
    )
    settings.save()
    console.print(create_table("Application Settings", settings.app.dict()))


@app.command()
def show_settings(
    setting_type: Optional[str] = typer.Option(
        None,
        help="Type of settings to show: 'db', 'storage', 'app', or leave empty for all",
    )
):
    """Display current settings."""
    settings.display_settings(setting_type)


@app.command()
def setup():
    """Perform all setups in a single window."""
    setup_db(interactive=True)
    setup_storage(interactive=True)
    setup_app(interactive=True)


if __name__ == "__main__":
    app()
