export default [
  {
    match: {
      // match everything
    },
    callback: {
      url: "http://resource/.mu/delta",
      method: "POST"
    },
    options: {
      resourceFormat: "v0.0.1",
      gracePeriod: 250,
      ignoreFromSelf: true
    }
  },
  {
    match: {
      predicate: {
        type: 'uri',
        value: 'http://www.w3.org/ns/adms#status'
      },
      object: {
        type: 'uri',
        value: 'http://kanselarij.vo.data.gift/release-task-statuses/ready-for-release'
      }
    },
    callback: {
      url: "http://dcat-dataset-publication/delta",
      method: "POST"
    },
    options: {
      resourceFormat: "v0.0.1",
      gracePeriod: 250,
      ignoreFromSelf: true
    }
  },
  {
    match: {
      predicate: {
        type: 'uri',
        value: 'http://www.w3.org/ns/adms#status'
      },
      object: {
        type: 'uri',
        value: 'http://kanselarij.vo.data.gift/release-task-statuses/not-started'
      }
    },
    callback: {
      url: "http://themis-same-as/delta",
      method: "POST"
    },
    options: {
      resourceFormat: "v0.0.1",
      gracePeriod: 250,
      ignoreFromSelf: true
    }
  }
];
