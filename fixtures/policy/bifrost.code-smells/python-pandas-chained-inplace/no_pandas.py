def not_pandas(store, mask):
    store.loc[mask].clean(inplace=True)
    store["k"].fillna(0, inplace=True)
    return store
