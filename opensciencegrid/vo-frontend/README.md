
# Scitokens

It is a hard requirment for VOs to supply their own `/usr/sbin/frontend_scitoken`.
This is typically a bind-mounted shell script, which takes three arguments
(audience, glideinsite, groupname), and produces a token on stdout. Here is an 
example script:

```
#!/bin/bash -x

SUBJECT="vofrontend-$2"
AUDIENCE="$1"
GROUP="$3"

KEY_FILE=/etc/condor/scitokens.pem
KEY_ID=1234
ISSUER="https://some-issuer/url"
SCOPE="compute.read compute.modify compute.create compute.cancel"
JWT_ID="$(uuidgen -r)"
WLCG_VER="1.0"
LIFETIME=3600

# create the token, echo it to stdout
exec scitokens-admin-create-token \
    --keyfile "$KEY_FILE" \
    --key_id "$KEY_ID" \
    --issuer "$ISSUER" \
    --lifetime "$LIFETIME" \
    sub="$SUBJECT" \
    aud="$AUDIENCE" \
    scope="$SCOPE" \
    jti="$JWT_ID" \
    wlcg.ver="$WLCG_VER"
```


