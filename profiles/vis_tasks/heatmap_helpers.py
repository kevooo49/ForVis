import numpy as np


def regrid_x(heatmap, step):
    step = int(step)
    new_indexes = np.asarray(list(range(0, heatmap.shape[0], step)))
    new_indexes = new_indexes[1:-1]
    new_heatmap = np.zeros((len(new_indexes), heatmap.shape[1]))

    zone_size = step
    zone_offset = int(zone_size//2)

    for variable_index in range(heatmap.shape[1]):
        for i, new_index in enumerate(new_indexes):
            batch = heatmap[new_index - zone_offset:new_index+zone_offset + 1, variable_index]
            new_heatmap[i][variable_index] = np.mean(batch)
    return new_heatmap


def regrid_y(heatmap, step):
    step = int(step)
    new_indexes = np.asarray(list(range(0, heatmap.shape[1], step)))
    new_indexes = new_indexes[1:-1]
    new_heatmap = np.zeros((heatmap.shape[0], len(new_indexes)))

    zone_size = step
    zone_offset = int(zone_size // 2)

    for clause_index in range(heatmap.shape[0]):
        for i, new_index in enumerate(new_indexes):
            batch = heatmap[clause_index, new_index - zone_offset:new_index + zone_offset + 1]
            new_heatmap[clause_index][i] = np.mean(batch)
    return new_heatmap
