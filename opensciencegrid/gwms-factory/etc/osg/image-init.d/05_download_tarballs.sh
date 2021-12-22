#!/bin/sh

mkdir -p /var/lib/gwms-factory/condor
pushd /var/lib/gwms-factory/condor/
if [ $? -ne 0 ]; then
    echo "Unable to chdir to /var/lib/gwms-factory/condor"
    exit 1
fi

platforms="${GWMS_SUPPORTED_PLATFORMS:-CentOS7 CentOS8 Debian10 Ubuntu18 Ubuntu20}"

condor_to_gwms_platform() {
case $1 in
  CentOS7)
    echo "rhel7,linux-rhel7,default"
    ;;
  CentOS8)
    echo "rhel8,linux-rhel8"
    ;;
  Debian10)
    echo "debian10,linux-debian10"
    ;;
  Ubuntu18)
    echo "ubuntu18,linux-ubuntu18"
    ;;
  Ubuntu20)
    echo "ubuntu20,linux-ubuntu20"
    ;;
esac
}

cat > condor_pubkeys << EOF
# curl 'https://research.cs.wisc.edu/htcondor/tarball/keys/HTCondor-9.0-Key'
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.22 (GNU/Linux)

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
EkvOhDkSry7PGGKCh8UI0nCxTv/zHk/bakOh
=OmEK
-----END PGP PUBLIC KEY BLOCK-----
# curl 'https://research.cs.wisc.edu/htcondor/tarball/keys/HTCondor-current-Key'
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.22 (GNU/Linux)

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
EiYFzGhdOFnSSIWaoGbhGGk0wgvHEQsrrnCU
=wu53
-----END PGP PUBLIC KEY BLOCK-----
EOF

cat condor_pubkeys | gpg --import

echo "Platforms requested: $platforms"

download_release_tarballs () {
    echo "Downloading all tarballs for $1"
    for release in $(curl https://research.cs.wisc.edu/htcondor/tarball/$1/ 2>/dev/null | grep '\[DIR\]' | tr '>' ' ' | tr '<' ' ' | tr -d '/' | awk '{print $11;}' | grep -v current); do

        if [ -f sha256sum.txt.$release ]; then
            echo "Using local copy of checksums for release $release"
        else
            echo -n "Downloading checksum file for release $release... "
            curl -sSf https://research.cs.wisc.edu/htcondor/tarball/$1/$release/release/sha256sum.txt.gpg > sha256sum.txt.gpg
            if [ $? -ne 0 ]; then
                rm sha256sum.txt.gpg
                echo "FAIL"
                continue
            else
                echo "OK"
            fi
            gpg --output sha256sum.txt.$release --decrypt sha256sum.txt.gpg
            if [ $? -ne 0 ]; then
                echo "FAIL: GPG error when extracting sha256sum's"
                exit 1
            fi
        fi

        for platform in $platforms; do

            prefix=condor-$release-x86_64_$platform-stripped
            filename=$prefix.tar.gz

            if [ -e gfactory-$prefix.tar.gz ]; then
                echo "Using cached tarfile: gfactory-$prefix.tar.gz"
                continue
            fi

            grep -q $filename sha256sum.txt.$release
            if [ $? -ne 0 ]; then
                echo "WARNING: $platform not supported for release $release"
                continue
            fi

            grep $filename sha256sum.txt.$release > sha256sum.txt.platform
            sha256sum -c sha256sum.txt.platform 2> /dev/null > /dev/null
            if [ $? -ne 0 ]; then

                echo -n "Downloading HTCondor $release for platform $platform... "
                url=https://research.cs.wisc.edu/htcondor/tarball/$1/$release/release/$filename
                curl -sSf $url > $filename
                if [ $? -ne 0 ]; then
                    rm $filename
                    echo "FAIL ($url)"
                else
                    echo "OK"
                fi

                echo -n "Verifying checksum: "
                sha256sum -c sha256sum.txt.platform
                if [ $? -ne 0 ]; then
                    echo "FAIL: Checksum incorrect on tarball $filename."
                    rm $filename
                else
                    echo "OK"
                fi

            else
                echo "Using cached HTCondor $release for platform $platform"
            fi

            echo "Repacking tarball to strip directory prefix."
            tar zxf $filename
            pushd condor-$release-*-x86_64_$platform-stripped >/dev/null
            tar zcf ../gfactory-$prefix.tar.gz.new *
            popd >/dev/null
            rm -rf condor-$release-*-x86_64_$platform-stripped
            mv gfactory-$prefix.tar.gz.new gfactory-$prefix.tar.gz
            echo "Done!  HTCondor $release / $platform available at gfactory-$prefix.tar.gz"

        done

    done
}

download_release_tarballs "stable"

lateststablerelease=$(ls gfactory-condor-*.tar.gz | grep $platform | sed 's|gfactory-condor-||' | tr '-' ' ' | awk '{print $1}' | tr '.' ' ' | grep '^. 0' | sort -k 3 -n | sort -k 2 -n | sort -k 1 -n | tail -n 1 | tr ' ' '.')

download_release_tarballs "feature"

output_file=/etc/gwms-factory/config.d/01-condor-tarballs.xml
echo "<glidein><condor_tarballs>" > $output_file
for platform in $platforms; do
    major=$(ls gfactory-condor-*.tar.gz | grep $platform | sed 's|gfactory-condor-||' | tr '-' ' ' | awk '{print $1}' | tr '.' ' ' | sort -k 3 -n | sort -k 2 -n | sort -k 1 -n | awk '{print $1}' | tail -n 1 | tr ' ' '.')
    latestmajorrelease=$(ls gfactory-condor-*.tar.gz | grep $platform | sed 's|gfactory-condor-||' | tr '-' ' ' | awk '{print $1}' | tr '.' ' ' | grep "^$major" | sort -k 3 -n | sort -k 2 -n | sort -k 1 -n | tail -n 1 | tr ' ' '.')
    gwms_platform=$(condor_to_gwms_platform $platform)

    for majorminorpatch in $(ls gfactory-condor-*.tar.gz | grep $platform | sed 's|gfactory-condor-||' | tr '-' ' ' | awk '{print $1}' | uniq | tr ' ' '.'); do
        latest_release=0
        for majorminor in $(ls gfactory-condor-*.tar.gz | grep $platform | sed 's|gfactory-condor-||' | tr '-' ' ' | awk '{print $1}' | tr '.' ' ' | sort -k 3 -n | sort -k 2 -n | sort -k 1 -n | awk '{print $1 " " $2}' | uniq | tr ' ' '.'); do
            latestmajorminorrelease=$(ls gfactory-condor-*.tar.gz | grep $platform | sed 's|gfactory-condor-||' | tr '-' ' ' | awk '{print $1}' | tr '.' ' ' | sort -k 3 -n | sort -k 2 -n | sort -k 1 -n | grep "^$majorminor" | tail -n 1 | tr ' ' '.')
            if [ "$lateststablerelease" == "$latestmajorminorrelease" -a "$majorminorpatch" == "$latestmajorminorrelease" ]; then
                echo "      <condor_tarball arch=\"default\" os=\"$gwms_platform\" tar_file=\"$PWD/gfactory-condor-$latestmajorminorrelease-x86_64_$platform-stripped.tar.gz\" version=\"default,$latestmajorminorrelease,$majorminor.x\"/>" >> $output_file
                latest_release=1
                break
            elif [ "$latestmajorrelease" == "$latestmajorminorrelease" -a "$majorminorpatch" == "$latestmajorminorrelease" ]; then
                echo "      <condor_tarball arch=\"default\" os=\"$gwms_platform\" tar_file=\"$PWD/gfactory-condor-$latestmajorminorrelease-x86_64_$platform-stripped.tar.gz\" version=\"$latestmajorminorrelease,$majorminor.x,$major.x.x\"/>" >> $output_file
                latest_release=1
                break
            elif [ "$majorminorpatch" == "$latestmajorminorrelease" ]; then 
                echo "      <condor_tarball arch=\"default\" os=\"$gwms_platform\" tar_file=\"$PWD/gfactory-condor-$latestmajorminorrelease-x86_64_$platform-stripped.tar.gz\" version=\"$latestmajorminorrelease,$majorminor.x\"/>" >> $output_file
                latest_release=1
                break
            fi
        done
        if [ $latest_release -eq 0 ]; then
            echo "      <condor_tarball arch=\"default\" os=\"$gwms_platform\" tar_file=\"$PWD/gfactory-condor-$majorminorpatch-x86_64_$platform-stripped.tar.gz\" version=\"$majorminorpatch\"/>" >> $output_file
        fi

    done
done
echo "</condor_tarballs></glidein>" >> $output_file

popd
