"""This module provides a test suite for the Calculation schemas at app.schemas.calculation"""
import pytest

from datetime import datetime
from pydantic import ValidationError
from uuid import UUID, uuid4

from app.schemas.calculation import CalculationForm, CalculationRecord

def test_calc_form_properties():
    """Validates CalculationForm properties and constructor"""
    data = {
        "type": "Addition",
        "inputs": [1, 2],
    }
    calc_form = CalculationForm(**data)
    assert isinstance(calc_form, CalculationForm)
    assert 1 in calc_form.inputs
    assert 2 in calc_form.inputs
    assert calc_form.type == "addition"

def test_calc_record_properties():
    """Validates CalculationRecord properties and constructor"""
    data = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "Addition",
        "inputs": [1, 2],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    calc_record = CalculationRecord(**data)
    assert isinstance(calc_record, CalculationRecord)
    assert isinstance(calc_record.id, UUID)
    assert isinstance(calc_record.user_id, UUID)
    assert 1 in calc_record.inputs
    assert 2 in calc_record.inputs
    assert isinstance(calc_record.created_at, datetime)
    assert isinstance(calc_record.updated_at, datetime)
