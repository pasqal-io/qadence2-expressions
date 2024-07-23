from __future__ import annotations

import pytest

from qadence2_expressions.support import Support


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
        Support(1, 2, target=(1, 2))

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


def test_support_overlap() -> None:
    s1 = Support(1, 2)
    s2 = Support(target=(2, 1), control=(3,))
    s3 = Support(3)

    assert s1.overlap_with(s2)
    assert not s1.overlap_with(s3)


def test_support_overlap_all() -> None:
    s1 = Support()
    s2 = Support(1)

    assert s1.overlap_with(s2)


def test_support_not_overlap() -> None:
    s1 = Support(1, 2)
    s2 = Support(3)

    assert not s1.overlap_with(s2)


def test_join_self() -> None:
    s = Support(target=(3,), control=(1, 2))

    assert s.join(s) == s


def test_join_target_all() -> None:
    s1 = Support(1)
    s2 = Support(target=(2, 3), control=(1,))

    assert s1.join(Support.target_all()) == Support.target_all()
    assert s2.join(Support.target_all()) == Support.target_all()


def test_join_target_control_overlap() -> None:
    s1 = Support(1, 3)
    s2 = Support(target=(3,), control=(1, 2))
    assert s1.join(s2) == Support(1, 2, 3)


def test_join() -> None:
    s1 = Support(target=(3,), control=(1, 2))
    s2 = Support(target=(0,), control=(1,))

    assert s1.join(s2) == Support(target=(0, 3), control=(1, 2))
