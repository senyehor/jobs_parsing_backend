from pydantic import BaseModel, HttpUrl


class JobSite(BaseModel):
    name: str
    slug: str
    description: str | None = None
    link: HttpUrl

    model_config = {"from_attributes": True}
