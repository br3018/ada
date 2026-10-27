package Model {
    public import PartLibrary::*;

    doc /* 
    * This package defines the model that uses the parts from the PartLibrary.
    */

    part def MyFluidSystem {
        doc /* Example part representing a fluid system using parts from the PartLibrary */
        part vessel : FluidVessel;
        part pipe : FluidPipe;
        part machine : FluidMachine;
        part valve : FluidValve;
        part fitting : FluidFitting;
        part sensor : FluidSensor;
    }

    part fluidSystem : MyFluidSystem;

} // package Model