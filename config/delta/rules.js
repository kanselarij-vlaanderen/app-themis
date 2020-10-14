export default [
  {
    match: {
      subject: { }
    },
    callback: {
      url: "http://resourcebackend/.mu/delta",
      method: "POST"
    },
    options: {
      resourceFormat: "v0.0.1",
      gracePeriod: 250,
      ignoreFromSelf: true
    }
  }
];