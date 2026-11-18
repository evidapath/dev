import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from us import major
U="https://college.harvard.edu/academics/liberal-arts-sciences/concentrations"; PG="4706502cf96b"
T="Concentrations | Harvard College"; O="Harvard College"
CQ='At Harvard College, students choose a "concentration," which is what we call a major.'
major("us-harvard","psychology",U,PG,T,O,[CQ,"Psychology B.A. Social Sciences","Psychology is the scientific study of the mind, and as such, we investigate the minds of humans and other species."],
      "Psychology","BA","Psychology","",4,"Psychology concentration (B.A.), Harvard College. The concentration (major) is chosen at Harvard College after admission.",
      "program-us-harvard-economics",CQ)
major("us-harvard","molecular-cellular-biology",U,PG,T,O,[CQ,"Molecular and Cellular Biology B.A. Sciences","Molecular and Cellular Biology is rooted in the investigation of biological processes based on the study of molecules and their interactions in the context of cells and tissues, and how the genome orchestrates cell behavior."],
      "Molecular and Cellular Biology","BA","Biology","",4,"Molecular and Cellular Biology concentration (B.A.), Harvard College. The concentration (major) is chosen at Harvard College after admission.",
      "program-us-harvard-economics",CQ)
print("ok")
