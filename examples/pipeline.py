from main import FurioPipeline as FURIO

for i in range(20, 50):
    FURIO.N_SAMPLES = i
    print(f"[START] - Running FURIO Pipeline for {i} samples.")
    data = FURIO.get_data(img_file='training_data/N (1).png')
    results = FURIO.evaluation(data)
    FURIO.plot_results(results)