import numpy as np
from sentence_transformers import util
from core.types import ImageData


class CommunityDetector:
    def __init__(
        self, threshold: float = 0.7, min_community_size: int = 2, init_max_size: int = 10
    ):
        self.threshold = threshold
        self.min_community_size = min_community_size
        self.init_max_size = init_max_size

        self.clusters = []
        self.centroids = []

    def fit(self, image_data: dict[str, ImageData]):
        ids = []
        embeddings = []
        face_ids = []
        for id, data in image_data.items():
            for face_id, face_data in data.faces.items():
                ids.append(id)
                embeddings.append(face_data["embedding"].flatten())
                face_ids.append(face_id)

        cos_scores = util.cos_sim(embeddings, embeddings)

        top_k_values, _ = cos_scores.topk(k=self.min_community_size, largest=True)

        extracted_communities = []
        for i in range(len(top_k_values)):
            if top_k_values[i][-1] >= self.threshold:
                new_cluster = []

                top_val_large, top_idx_large = cos_scores[i].topk(
                    k=self.init_max_size, largest=True
                )
                top_idx_large = top_idx_large.tolist()
                top_val_large = top_val_large.tolist()

                if top_val_large[-1] < self.threshold:
                    for idx, val in zip(top_idx_large, top_val_large):
                        if val < self.threshold:
                            break

                        new_cluster.append(idx)
                else:
                    for idx, val in enumerate(cos_scores[i].tolist()):
                        if val >= self.threshold:
                            new_cluster.append(idx)

                extracted_communities.append(new_cluster)

        extracted_communities = sorted(extracted_communities, key=lambda x: len(x), reverse=True)

        unique_communities = []
        extracted_ids = set()

        for community in extracted_communities:
            add_cluster = True
            for idx in community:
                if idx in extracted_ids:
                    add_cluster = False
                    break

            if add_cluster:
                unique_communities.append(community)
                for idx in community:
                    extracted_ids.add(idx)

        cluster_embeddings = []
        for cluster in unique_communities:
            temp = []
            for c in cluster:
                temp.append(embeddings[c])
            cluster_embeddings.append(temp)

        cluster_centroids = []
        for cluster in cluster_embeddings:
            cluster_centroids.append(np.mean(cluster, axis=0))

        similar_centroid_map = {}
        for i, c in enumerate(cluster_centroids):
            temp = []
            for j, c2 in enumerate(cluster_centroids):
                if i != j:
                    temp.append((j, util.cos_sim(c, c2)[0][0].item()))
            temp = sorted(temp, key=lambda x: x[1], reverse=True)
            similar_centroid_map[i] = temp[:3]

        new_clusters = []
        threshold = 0.7
        seen = set()
        for i, c in enumerate(cluster_centroids):
            for j, sim in similar_centroid_map[i]:
                if sim > threshold and j not in seen:
                    new_clusters.append(unique_communities[i] + unique_communities[j])
                    seen.add(j)
                    seen.add(i)
            if i not in seen:
                new_clusters.append(unique_communities[i])

        new_centroids = []
        for cluster in new_clusters:
            temp = []
            for c in cluster:
                temp.append(embeddings[c])
            new_centroids.append(np.mean(temp, axis=0))

        self.centroids = new_centroids

        cluster_index_transforms = []
        for idx, cluster in enumerate(new_clusters):
            temp = dict()
            for c in cluster:
                if ids[c] not in temp:
                    temp[ids[c]] = {
                        "face_id": face_ids[c],
                        "embedding": embeddings[c],
                    }
                else:
                    seem_emb = temp[ids[c]]["embedding"]
                    curr_emb = embeddings[c]
                    cluster_centr = new_centroids[idx]
                    cos_sim_seem = util.cos_sim(seem_emb, cluster_centr)[0][0].item()
                    cos_sim_curr = util.cos_sim(curr_emb, cluster_centr)[0][0].item()

                    if cos_sim_curr > cos_sim_seem:
                        temp[ids[c]] = {
                            "face_id": face_ids[c],
                            "embedding": embeddings[c],
                        }
            temp = [(k, v["face_id"]) for k, v in temp.items()]
            cluster_index_transforms.append(temp)

        self.clusters = cluster_index_transforms

    def fit_predict(self, image_data_list: dict[str, ImageData]):
        self.fit(image_data_list)
        return self.clusters

    def predict(self, image_data_list: dict[str, ImageData]):
        return self.fit_predict(image_data_list)


# def community_detection(
#     image_data_list: list[ImageData],
#     threshold: float,
#     min_community_size: int = 2,
#     init_max_size: int = 500,
# ):

#     id_embeddings = [
#         (image_data.id, image_data.faces[key]["embedding"])
#         for image_data in image_data_list
#         for key in image_data.faces
#     ]
#     ids = [id for id, _ in id_embeddings]
#     embeddings = [embedding for _, embedding in id_embeddings]

#     cos_scores = util.cos_sim(embeddings, embeddings)

#     top_k_values, _ = cos_scores.topk(k=min_community_size, largest=True)

#     extracted_communities = []
#     for i in range(len(top_k_values)):
#         if top_k_values[i][-1] >= threshold:
#             new_cluster = []

#             top_val_large, top_idx_large = cos_scores[i].topk(k=init_max_size, largest=True)
#             top_idx_large = top_idx_large.tolist()
#             top_val_large = top_val_large.tolist()

#             if top_val_large[-1] < threshold:
#                 for idx, val in zip(top_idx_large, top_val_large):
#                     if val < threshold:
#                         break

#                     new_cluster.append(idx)
#             else:
#                 for idx, val in enumerate(cos_scores[i].tolist()):
#                     if val >= threshold:
#                         new_cluster.append(idx)

#             extracted_communities.append(new_cluster)

#     extracted_communities = sorted(extracted_communities, key=lambda x: len(x), reverse=True)

#     unique_communities = []
#     extracted_ids = set()

#     for community in extracted_communities:
#         add_cluster = True
#         for idx in community:
#             if idx in extracted_ids:
#                 add_cluster = False
#                 break

#         if add_cluster:
#             unique_communities.append(community)
#             for idx in community:
#                 extracted_ids.add(idx)

#     unique_communities = [[ids[idx] for idx in community] for community in unique_communities]

#     return unique_communities
