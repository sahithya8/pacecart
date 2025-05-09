import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Concatenate, Dense

# Initialize logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Simple neural network for utility score prediction
def build_utility_model(num_users, num_products, embedding_dim=50):
    user_input = Input(shape=(1,), name='user_id')
    product_input = Input(shape=(1,), name='product_id')
    
    user_embedding = Embedding(num_users, embedding_dim, name='user_embedding')(user_input)
    product_embedding = Embedding(num_products, embedding_dim, name='product_embedding')(product_input)
    
    user_flat = Flatten()(user_embedding)
    product_flat = Flatten()(product_embedding)
    
    concat = Concatenate()([user_flat, product_flat])
    
    dense1 = Dense(128, activation='relu')(concat)
    dense2 = Dense(64, activation='relu')(dense1)
    output = Dense(1, activation='sigmoid')(dense2)
    
    model = Model(inputs=[user_input, product_input], outputs=output)
    model.compile(optimizer='adam', loss='mse')
    
    return model

# Cache model
UTILITY_MODEL = None
NUM_USERS = 1000  # Adjust based on your dataset
NUM_PRODUCTS = 5000  # Adjust based on your dataset

# Predict utility scores using deep learning
def predict_utility_scores(user_id, product_ids, products_df):
    global UTILITY_MODEL

    # Build product ID to index map
    unique_ids = sorted(products_df['product_id'].unique())
    id_to_index = {pid: idx for idx, pid in enumerate(unique_ids)}

    # Map the incoming product_ids to valid indices
    mapped_ids = [id_to_index[pid] for pid in product_ids if pid in id_to_index]

    if UTILITY_MODEL is None:
        logger.debug("Initializing utility model...")
        num_products = len(unique_ids)
        UTILITY_MODEL = build_utility_model(NUM_USERS, num_products)

        # Dummy training (replace with real training logic)
        dummy_user_ids = np.array([user_id] * len(mapped_ids))
        dummy_product_ids = np.array(mapped_ids)
        dummy_scores = np.random.uniform(0, 1, len(mapped_ids))
        UTILITY_MODEL.fit([dummy_user_ids, dummy_product_ids], dummy_scores, epochs=1, verbose=0)

    try:
        user_ids = np.array([user_id] * len(mapped_ids))
        product_ids = np.array(mapped_ids)

        scores = UTILITY_MODEL.predict([user_ids, product_ids], verbose=0).flatten()
        logger.debug(f"Deep learning scores for user {user_id}: {scores.tolist()}")
        return scores
    except Exception as e:
        logger.error(f"Deep learning prediction failed: {e}")
        return np.ones(len(mapped_ids)) * 0.5  # fallback score
