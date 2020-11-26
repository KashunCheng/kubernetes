{
  apiVersion: 'argoproj.io/v1alpha1',
  kind: 'Application',
  metadata: {
    name: 'coredns',
  },
  spec: {
    destination: {
      namespace: 'kube-system',
      server: 'https://kubernetes.default.svc',
    },
    project: 'default',
    source: {
      path: 'core/coredns',
      repoURL: 'https://github.com/ocf/kubernetes',
      targetRevision: 'HEAD',
      helm: {
        valueFiles: [
          'values.yaml',
        ],
        version: 'v3',
      },
    },
  },
}
