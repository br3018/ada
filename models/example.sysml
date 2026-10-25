package Example {
    private import ScalarValues::Real;

    part def Vehicle {
        attribute mass : Real;
        part engine : Engine;
        part wheels : Wheel[4];
    }

    part def Engine {
        attribute power : Real;
    }

    part def Wheel {
        attribute diameter : Real;
    }

    part car : Vehicle {
        attribute redefines mass = 1200.0;
    }
}
