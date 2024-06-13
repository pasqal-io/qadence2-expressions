use num::Complex;
use std::ops;

pub enum Numerical {
    Int(i64),
    Float(f64),
    Complex(Complex<f64>),
}

pub enum Numeric {
    Int(i64),
    Float(f64),
    Complex(Complex<f64>),
}

impl ops::Add<Numeric> for Numeric {
    // type Output = FooBar;

    fn add(self, _rhs: Numeric) -> Numeric {
        println!("> Foo.add(Bar) was called");
	self + _rhs
    }
}



pub struct Symbol {
    name: &'static str
}


#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_numeric() {
        assert_eq!(Operator::ADD.as_str(), "+");
        // assert_eq!(Operator::MUL.as_str(), "*");
        // assert_eq!(Operator::NONCOMMUTE.as_str(), "@");
        // assert_eq!(Operator::POWER.as_str(), "^");
        // assert_eq!(Operator::CALL.as_str(), "call");
    }
}
