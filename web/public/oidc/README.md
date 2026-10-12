# ServiceAccount issuers

Each directory is one Hangar cluster's ServiceAccount token issuer: `https://hangarplatform.dev/oidc/<cluster>`.
Its `.well-known/openid-configuration` and `jwks.json` hold public keys only. Other clusters' API servers fetch them
to accept that cluster's short-lived ServiceAccount tokens (apron `docs/cluster-identity.md`).

Regenerate with apron's `hack/cluster-identity.sh publish --context <cluster> --issuer
https://hangarplatform.dev/oidc/<cluster> --out web/public/oidc/<cluster>`. Do it again whenever a cluster's
`sa.key` changes; until then, every token from that cluster fails on the clusters that trust it.
