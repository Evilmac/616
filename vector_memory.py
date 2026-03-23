# Minimal vector_memory.py with optional faiss backend and NumPy fallback.
# Provides a simple VectorMemory class with methods:
#  - add(vectors, ids=None)
#  - search(query_vectors, k=5) -> (ids_list, distances_list)
# This file is dependency-light: uses faiss if available, otherwise a NumPy brute-force backend.

import numpy as np

try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    faiss = None
    _FAISS_AVAILABLE = False

class VectorMemory:
    def __init__(self, dim=None, index_factory="Flat"):
        """
        dim: dimensionality of vectors (required for faiss backend when creating index).
        index_factory: faiss index factory string (only used if faiss is available).
        """
        self.dim = dim
        self.ids = []        # list of ids corresponding to stored vectors
        self.vectors = None  # numpy array of shape (n, dim) for fallback
        self._faiss_index = None
        self._index_factory = index_factory

        if _FAISS_AVAILABLE:
            # will create index on first add when dim is known
            self._faiss_index = None

    # ---- Add vectors ----
    def add_text(self, vectors, ids=None):
        """
        vectors: array-like shape (n, dim)
        ids: optional list of identifiers for each vector (length n).
        """
        arr = np.asarray(vectors, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        if ids is None:
            # generate incremental ids if not provided
            start = len(self.ids)
            ids = [start + i for i in range(arr.shape[0])]
        else:
            ids = list(ids)

        if _FAISS_AVAILABLE:
            # ensure dim known
            if self.dim is None:
                self.dim = arr.shape[1]
            if self._faiss_index is None:
                # create index
                try:
                    self._faiss_index = faiss.index_factory(self.dim, self._index_factory)
                except Exception:
                    # fallback to IndexFlatL2 if factory fails
                    self._faiss_index = faiss.IndexFlatL2(self.dim)
            # add vectors to faiss index
            self._faiss_index.add(arr)
            self.ids.extend(ids)
        else:
            # NumPy fallback: append to vectors array
            if self.vectors is None:
                self.vectors = arr.copy()
            else:
                self.vectors = np.vstack([self.vectors, arr])
            self.ids.extend(ids)

    # ---- Search ----
    def search(self, query_vectors, k=5):
        """
        query_vectors: array-like shape (m, dim) or (dim,)
        returns: (list_of_id_lists, list_of_distance_lists)
                 Each inner list has length up to k (if fewer vectors stored, returns fewer).
        """
        q = np.asarray(query_vectors, dtype=np.float32)
        if q.ndim == 1:
            q = q.reshape(1, -1)

        if _FAISS_AVAILABLE and self._faiss_index is not None:
            # faiss returns (distances, indices)
            D, I = self._faiss_index.search(q, k)
            result_ids = []
            result_dists = []
            for row_idx in range(I.shape[0]):
                ids_row = []
                d_row = []
                for j, idx in enumerate(I[row_idx]):
                    if idx < 0 or idx >= len(self.ids):
                        continue
                    ids_row.append(self.ids[int(idx)])
                    d_row.append(float(D[row_idx, j]))
                result_ids.append(ids_row)
                result_dists.append(d_row)
            return result_ids, result_dists
        else:
            # NumPy brute-force L2 distances
            if self.vectors is None or self.vectors.shape[0] == 0:
                return [[] for _ in range(q.shape[0])], [[] for _ in range(q.shape[0])]
            # compute squared L2 distances
            # broadcasting: (m,1,d) vs (1,n,d) -> (m,n,d)
            # but use efficient formula: ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b
            a2 = np.sum(q * q, axis=1, keepdims=True)  # (m,1)
            b2 = np.sum(self.vectors * self.vectors, axis=1)  # (n,)
            ab = np.dot(q, self.vectors.T)  # (m,n)
            d2 = a2 + b2 - 2 * ab
            # numeric issues
            d2 = np.maximum(d2, 0.0)
            ids_list = []
            dists_list = []
            for i in range(d2.shape[0]):
                row = d2[i]
                idx_sorted = np.argsort(row)[:k]
                ids_row = [self.ids[int(idx)] for idx in idx_sorted]
                d_row = [float(np.sqrt(row[int(idx)])) for idx in idx_sorted]  # return L2 distance
                ids_list.append(ids_row)
                dists_list.append(d_row)
            return ids_list, dists_list

    # ---- Utility ----
    def reset(self):
        self.ids = []
        self.vectors = None
        self._faiss_index = None

    def __len__(self):
        return len(self.ids)