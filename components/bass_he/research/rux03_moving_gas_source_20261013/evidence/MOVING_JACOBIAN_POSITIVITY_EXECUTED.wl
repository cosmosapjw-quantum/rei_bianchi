ClearAll["Global`*"];
started=AbsoluteTime[];
factor=(ar gg+alpha pp gg^2)^2 (ar(alpha-1)gg^3+alpha pp((alpha-2)gg^4+gg^2));
poly=Expand[factor/.alpha->2+aex];
coefficients=Last/@CoefficientRules[poly,{ar,pp,gg,aex}];
strictMonomial=Coefficient[Coefficient[poly/.{pp->0,aex->0},ar,3],gg,5];
check=And@@Thread[coefficients>=0]&&strictMonomial===1;
ExportString[<|"unit"->"HERE_RUX03_MOVING_GAS_SOURCE_05","version"->$Version,
"systemID"->$SystemID,"elapsedSeconds"->AbsoluteTime[]-started,
"checks"-><|"primitive_jacobian_positive"->TrueQ[check]|>,
"checkCount"->1,"passCount"->If[TrueQ[check],1,0],"allPass"->TrueQ[check],
"nonnegativeCoefficients"->coefficients,"strictMonomial"->"ar^3 gg^5 with coefficient 1",
"domain"->"ar>0, gg>=1, pp>=0, aex=alpha-2>=0",
"logic"->"Every monomial is nonnegative on the domain; the displayed monomial is strictly positive. This certifies the unchanged determinant factor.",
"replacesUnresolvedAssertion"->"MOVING_SOURCE_EXACT_RESULT_v1.json:primitive_jacobian_positive",
"failureClass"->"FullSimplify retained a conditional inequality; TrueQ labeled that unresolved assertion false. No negative determinant or counterexample was returned."|>,"RawJSON"]