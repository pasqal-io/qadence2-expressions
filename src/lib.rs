use pyo3::prelude::*;

mod expression;
// use expression::Operator;

#[pyclass]
pub enum Operator {
    ADD,
    MUL,
    NONCOMMUTE,
    POWER,
    CALL,
}

impl Operator {
    pub fn as_str(&self) -> &'static str {
        match self {
            Operator::ADD => "+",
	    Operator::MUL => "*",
	    Operator::NONCOMMUTE => "@",
	    Operator::POWER => "^",
	    Operator::CALL => "call",
        }
    }
}


/// Formats the sum of two numbers as string.
#[pyfunction]
fn operator() -> PyResult<&'static str> {
    Ok(Operator::ADD.as_str())
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn pyexpression(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(operator, m)?)?;
    Ok(())
}
