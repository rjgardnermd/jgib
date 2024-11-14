import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Type, TypeVar

load_dotenv(override=True)

T = TypeVar("T", bound=BaseModel)


def loadEnv(pydanticModel: Type[T]) -> T:
    """
    Load environment variables into a given Pydantic model.

    Args:
        model (Type[T]): A Pydantic model class.

    Returns:
        T: An instance of the model populated with environment variables.
    """
    # Extract environment variables for each field in the model
    env_values = {
        field_name: os.getenv(field_name)
        for field_name in pydanticModel.model_fields.keys()
    }

    # Create an instance of the model with loaded environment variables
    config = pydanticModel(**env_values)

    return config
