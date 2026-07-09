from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    food_id: int
    food_name: str
    meal_role: str
    serving_g: float = Field(ge=0)
    kcal: float = Field(ge=0)
    carbohydrate: float = Field(ge=0)
    protein: float = Field(ge=0)
    fat: float = Field(ge=0)
    sugar: float = Field(ge=0)
    sodium: float = Field(ge=0)


class NutritionSummary(BaseModel):
    kcal: float = 0
    carbohydrate: float = 0
    protein: float = 0
    fat: float = 0
    sugar: float = 0
    sodium: float = 0


class MealRequest(BaseModel):
    query: str = ""
    target_kcal: float | None = Field(default=None, gt=0)
    limit: int = Field(default=10, gt=0)


class MealPlan(BaseModel):
    foods: list[FoodItem]
    total_nutrition: NutritionSummary
    notes: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    is_valid: bool
    reasons: list[str] = Field(default_factory=list)


class MockAgentResult(BaseModel):
    request: MealRequest
    candidates: list[FoodItem]
    meal_plan: MealPlan
    validation: ValidationResult
