from __future__ import annotations

import pytest

from qadence2_expressions.expr.qubit_support import Support


def test_support_single_qubit_initialization() -> None:
    s1 = Support(1)
    s2 = Support(target=(1,))

    assert s1 == s2

def test_support_multiple_qubit_initialization() -> None:
    s1 = Support(1, 2, 3)
    s2 = Support(target=(1, 2, 3))

    assert s1 == s2

def test_support_all_qubit_initialization() -> None:
    s1 = Support.target_all()
    s2 = Support(target=())

    assert s1 == Support()
    assert s1 == s2

def test_controlled_support_initialization() -> None:
    s1 = Support(target=(1,), control=(0,))
    s2 = Support(control=(0,), target=(1,))

    assert s1 == s2


def test_intialization_index_target_control_error() -> None:
    with pytest.raises(SyntaxError) as error:
        Support(1, 2, target=(1,), control=(2,))
    
    assert str(error.value) == "Please, provide either qubit indices or target-control tuples"

def test_intialization_index_target_error() -> None:
    with pytest.raises(SyntaxError) as error:
        Support(1, 2, target=(1,2))
    
    assert str(error.value) == "Please, provide either qubit indices or target-control tuples"

def test_intialization_index_target_error() -> None:
    with pytest.raises(SyntaxError) as error:
        Support(1, 2, control=(2,))
    
    assert str(error.value) == "Please, provide either qubit indices or target-control tuples"


def test_intialization_missing_target_error() -> None:
    with pytest.raises(SyntaxError) as error:
        Support(control=(2,))
    
    assert str(error.value) == "A controlled operation needs both, control and target."


def test_intialization_target_control_overlap_error() -> None:
    with pytest.raises(SyntaxError) as error:
        Support(control=(1, 2), target=(2, 3))
    
    assert str(error.value) == "Target and control indices cannot overlap."


def test_support_order() -> None:
    s1 = Support(1, 2, 3)
    s2 = Support(3, 4)

    assert s1 < s2

def test_support_order_target_control() -> None:
    s1 = Support(target=(1, 2), control=(3,))
    s2 = Support(target=(3, 4))

    assert s1 < s2

def test_support_order_same_target() -> None:
    s1 = Support(target=(1, 3), control=(4,))
    s2 = Support(target=(1, 3), control=(2, 5))

    assert s1 > s2