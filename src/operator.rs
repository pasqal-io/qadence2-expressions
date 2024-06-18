#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Operator {
    ADD,
    CALL,
    MUL,
    NONCOMMUTE,
    POWER,
}

impl Operator {
    pub fn as_str(&self) -> &'static str {
        match self {
            Operator::ADD => "+",
	    Operator::CALL => "call",
	    Operator::MUL => "*",
	    Operator::NONCOMMUTE => "@",
	    Operator::POWER => "^",
        }
    }
}


#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_operator_as_str() {
        assert_eq!(Operator::ADD.as_str(), "+");
        assert_eq!(Operator::MUL.as_str(), "*");
        assert_eq!(Operator::NONCOMMUTE.as_str(), "@");
        assert_eq!(Operator::POWER.as_str(), "^");
        assert_eq!(Operator::CALL.as_str(), "call");
    }
}
