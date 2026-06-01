import ROOT

input_filename = "DP1_folder/AToGG_GEN_E_new_all_10k_phase1_analysis.root"
infile = ROOT.TFile.Open(input_filename, "READ")
tree = infile.Get("demo/T")

if not tree:
    print("Error: TTree 'demo/T' not found! Checking directory contents:")
    infile.ls()
    exit(1)

print("--- Verifying Stored Gen-Sim Tracking Branches ---")
num_entries = tree.GetEntries()
print("Total entries stored: {}".format(num_entries))

for entry in range(min(3, num_entries)):
    print("\n=== Event {} ===".format(entry))
    tree.GetEntry(entry)
    
    print("Run: {}, Event: {}, Lumi: {}".format(tree.run, tree.event, tree.lumi))
    
    n_particles = len(tree.GenPart_pdgId)
    print("Number of gen particles found in this event: {}".format(n_particles))
    
    print("{:<10} {:<10} {:<15} {:<15}".format("Index", "PDG ID", "Status", "Mother PDG ID"))
    print("-" * 55)
    
    for i in range(min(15, n_particles)):
        print("{:<10} {:<10} {:<15} {:<15}".format(
            i, 
            tree.GenPart_pdgId[i], 
            tree.GenPart_status[i], 
            tree.GenPart_motherPdgId[i]
        ))
        
    if n_particles > 15:
        print("... and {} more particles".format(n_particles - 15))

infile.Close()