import FWCore.ParameterSet.Config as cms
from GeneratorInterface.EvtGenInterface.EvtGenSetting_cff import *
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8GeneratorFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    pythiaHepMCVerbosity = cms.untracked.bool(True),
    comEnergy = cms.double(13000.0),

    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'SoftQCD:nonDiffractive = on',
			'PTFilter:filter = on', # this turn on the filter
            'PTFilter:quarkToFilter = 5', # PDG id of q quark
            'PTFilter:scaleToFilter = 1.0',
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CP5Settings',
            'processParameters',
        ),
    ),

    ExternalDecays = cms.PSet(
        EvtGen130 = cms.untracked.PSet(
            decay_table            = cms.string('GeneratorInterface/EvtGenInterface/data/DECAY_2014_NOLONGLIFE.DEC'),
            particle_property_file = cms.FileInPath('GeneratorInterface/EvtGenInterface/data/evt_2014.pdl'),
            list_forced_decays     = cms.vstring(
                'MyB+',
                'MyB-',
                'MyBc+',
                'MyBc-',
                'Myanti-B0',
                'MyB0',
                'Myanti-Bs',
                'MyBs',
                'MyLambda_b0',
                'MyXi_b-',
                'Myanti-Xi_b+',
                'MyXi_b0',
                'Myanti-Xi_b0',
                'MyOmega_b-',
                'Myanti-Omega_b+',
            ),        
            operates_on_particles  = cms.vint32(),    
            convertPythiaCodes     = cms.untracked.bool(False),
            user_decay_file        = cms.vstring('GeneratorInterface/ExternalDecays/data/HbToJpsiMuMuInclusive.dec'),
        ),
        parameterSets = cms.vstring('EvtGen130'),
    ),

)

jpsi_from_b_hadron_filter = cms.EDFilter(
    "PythiaFilterMultiAncestor",
    ParticleID      = cms.untracked.int32 (443),
    MinPt           = cms.untracked.double( 6.),
    MinEta          = cms.untracked.double(-3.),
    MaxEta          = cms.untracked.double( 3.),
    MotherIDs       = cms.untracked.vint32([5]),
    DaughterIDs     = cms.untracked.vint32([-13, 13]),
    DaughterMinPts  = cms.untracked.vdouble([ 2.8 , 2.8  ]),
    DaughterMaxPts  = cms.untracked.vdouble([ 1.e6,  1.e6]),
    DaughterMinEtas = cms.untracked.vdouble([-2.52 , -2.52 ]),
    DaughterMaxEtas = cms.untracked.vdouble([ 2.52 ,  2.52 ]),
)

three_mu_filter = cms.EDFilter(
    "MCMultiParticleFilter",
    NumRequired = cms.int32(3),
    AcceptMore  = cms.bool(True),
    ParticleID  = cms.vint32(13,13,13),
    PtMin       = cms.vdouble(2.8, 2.8, 2.),
    EtaMax      = cms.vdouble(2.52, 2.52, 2.52),
    Status      = cms.vint32(1, 1, 1),
)

# jpsi_mu_filter = cms.EDFilter(
#     "MCParticlePairFilter",
#     particleID1    = cms.untracked.vint32(443), # jpsi
#     particleID2    = cms.untracked.vint32(13), # mu
#     ParticleCharge = cms.untracked.int32(1), # faulty logic, cases with one neutral and one charged particle not considered https://github.com/cms-sw/cmssw/blob/master/GeneratorInterface/GenFilters/plugins/MCParticlePairFilter.cc#L229 https://github.com/cms-sw/cmssw/blob/master/GeneratorInterface/GenFilters/plugins/MCParticlePairFilter.cc#L240
#     MinInvMass     = cms.untracked.double(3.097 + 0.105 + 0.05), # minimum invariant mass must be > mass(jpsi) + mass(mu) + epsilon, otherwise it always picks one of the jpsi's muons
#     MaxInvMass     = cms.untracked.double(10.),
#     MinDeltaR      = cms.untracked.double(0.01),
#     MinPt          = cms.untracked.vdouble(6., 2.),
#     MinEta         = cms.untracked.vdouble(-3., -2.52),
#     MaxEta         = cms.untracked.vdouble( 3.,  2.52),
#     Status         = cms.untracked.vint32(2, 1),
# )

# two OS muons make the Jpsi, so, if  there's an additional muon around
# it must have the same charge as that of to one of the Jpsi muons.
# In addition, the invariant mass of these two can't be too large 
mu_mu_same_charge_filter = cms.EDFilter(
    "MCParticlePairFilter",
    ParticleID1    = cms.untracked.vint32(13), # mu
    ParticleID2    = cms.untracked.vint32(13), # mu
    ParticleCharge = cms.untracked.int32(1), # same charge
    MaxInvMass     = cms.untracked.double(10.),
    MinPt          = cms.untracked.vdouble(2.8, 2.),
    MinEta         = cms.untracked.vdouble(-2.52, -2.52),
    MaxEta         = cms.untracked.vdouble( 2.52,  2.52),
    Status         = cms.untracked.vint32(1, 1),
)

configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('\$Revision$'),
    name = cms.untracked.string('\$Source$'),
    annotation = cms.untracked.string(
        'QCD bbbar production, '\
        'Jpsi from any b-hadron (either directly or feeddown), '\
        'Jpsi->mumu, mu pt>2.8, mu |eta|<2.52, '\
        'additional mu with pt>2. and |eta|<2.52, '\
        'invariannt mass(Jpsi, mu)<10, '\
        '13 TeV, '\
        'TuneCP5'
    )
)

ProductionFilterSequence = cms.Sequence(generator*jpsi_from_b_hadron_filter*three_mu_filter*mu_mu_same_charge_filter)
# ProductionFilterSequence = cms.Sequence(generator*jpsi_from_b_hadron_filter*three_mu_filter*jpsi_mu_filter)
# ProductionFilterSequence = cms.Sequence(generator*jpsi_from_b_hadron_filter*jpsi_mu_filter)
