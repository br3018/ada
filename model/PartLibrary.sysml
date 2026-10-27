package PartLibrary {
    public import ScalarValues::*;
    
    public import ISQ::MassValue;
    public import ISQ::PressureValue;

    public import SI::kg;
    public import SI::W;
    public import SI::m;
    public import SI::s;
    public import SI::Pa;

    doc /* 
    * This package defines the base classes for parts in the model.
    */
    
    part def FluidPart {
        doc /* Generic base part for all fluid parts */
        attribute meop : PressureValue;
        attribute mass : MassValue;
    }

    part def FluidVessel specializes FluidPart {
        doc /* Part representing a vessel for containing fluids */
    }
    part def FluidPipe specializes FluidPart {
        doc /* Part representing a pipe for transporting fluids */
    }
    part def FluidMachine specializes FluidPart {
        doc /* Part representing a machine that interacts with fluids */
    }
    part def FluidValve specializes FluidPart {
        doc /* Part representing a valve for controlling fluid flow */
    }
    part def FluidFitting specializes FluidPart {
        doc /* Part representing a fitting for connecting fluid components */
    }
    part def FluidSensor specializes FluidPart {
        doc /* Part representing a sensor for measuring fluid properties */
    }
} // package PartLibrary
