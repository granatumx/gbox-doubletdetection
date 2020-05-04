import granatum_sdk
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from doubletdetection.doubletdetection import doubletdetection
from scipy.sparse import scr_matrix


def main():
    gn = granatum_sdk.Granatum()

    assay = gn.get_import('assay')
    data =  np.array(assay.get('matrix'))

    seed = gn.get_arg('seed')

    #dense to sparse
    data = sparse.csr_matrix(data)

    zero_genes = (np.sum(data, axis=0) == 0).A.ravel()
    data = data[:, ~zero_genes]
    clf = doubletdetection.BoostClassifier(n_iters=50, use_phenograph=False, standard_scaling=True)
    doublets = clf.fit(data).predict(p_thresh=1e-16, voter_thresh=0.5)

    print("Convergence of doublet calls")
    f2, umap_coords = doubletdetection.plot.umap_plot(data, doublets, random_state=1, show=True)
    
    #doublet_index = np.where(doublets==1)[0]+1 #1-based indexing
    
    doublet_index = ["Singlet" if i == 0 else "Doublet" for i in doublets]

    gn.add_result(
        {
            'orient': 'split',
            'columns': ['Sample ID', 'Doublet/Singlet'],
            'data': [[x, y] for x, y in zip(assay.get('sampleIds'), doublet_index)],
        },
        'table',
    )

    gn.export_statically(assay, 'Assay')


    gn.commit()


if __name__ == "__main__":
    main()
