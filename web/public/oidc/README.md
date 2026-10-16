# ServiceAccount issuers

Each directory is one Hangar cluster's ServiceAccount token issuer: `https://hangarplatform.dev/oidc/<cluster>`.
Its `.well-known/openid-configuration` and `jwks.json` hold public keys only. Other clusters' API servers fetch them
to accept that cluster's short-lived ServiceAccount tokens (apron `docs/cluster-identity.md`), and AWS STS fetches them
for IAM roles that trust the cluster through an IAM OIDC provider (IRSA without EKS).

| Cluster | Trusted by |
|---|---|
| `kind-prod` | kiac-dev's API server (Tower reads and writes) |
| `kiac-dev` | Fulcio on kiac-dev (keyless signing); AWS IAM, for Crossplane's AWS providers (planned) |

The site workflow deploys these dotfiles only because `upload-pages-artifact` has `include-hidden-files: true`, and its
deploy job fails if any issuer here stops serving a discovery document that names itself.

Regenerate with apron's `hack/cluster-identity.sh publish --context <cluster> --issuer
https://hangarplatform.dev/oidc/<cluster> --out web/public/oidc/<cluster>`. Do it again whenever a cluster's
`sa.key` changes; until then, every token from that cluster fails everywhere that trusts it. AWS caches keys, so
keep the old key in `jwks.json` next to the new one until the cluster has switched.
