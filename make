#0 building with "default" instance using docker driver

#1 [project internal] load build definition from Dockerfile
#1 transferring dockerfile: 2.98kB done
#1 DONE 0.0s

#2 [project internal] load .dockerignore
#2 transferring context: 2B done
#2 DONE 0.0s

#3 [dagit internal] load build definition from Dockerfile
#3 transferring dockerfile: 2.98kB done
#3 DONE 0.0s

#4 [dagit internal] load .dockerignore
#4 transferring context: 2B done
#4 DONE 0.0s

#5 [content internal] load .dockerignore
#5 transferring context: 2B done
#5 DONE 0.0s

#6 [content internal] load build definition from Dockerfile
#6 transferring dockerfile: 2.98kB done
#6 DONE 0.0s

#7 [challenge internal] load .dockerignore
#7 transferring context: 2B done
#7 DONE 0.0s

#8 [challenge internal] load build definition from Dockerfile
#8 transferring dockerfile: 2.98kB done
#8 DONE 0.0s

#9 [dagster-daemon internal] load .dockerignore
#9 transferring context: 2B done
#9 DONE 0.0s

#10 [dagster-daemon internal] load build definition from Dockerfile
#10 transferring dockerfile: 2.98kB done
#10 DONE 0.0s

#11 [challenge internal] load metadata for docker.io/library/python:3.8.5-slim
#11 DONE 0.5s

#12 [content base 1/1] FROM docker.io/library/python:3.8.5-slim@sha256:502cd057453744145010eceb5a4af1e4f04ebed54f6e1e8d23d29ebe2afdbe6d
#12 DONE 0.0s

#13 [challenge internal] load build context
#13 transferring context: 1.70kB 0.0s done
#13 DONE 0.0s

#14 [content internal] load build context
#14 transferring context: 30.60kB 0.0s done
#14 DONE 0.0s

#15 [dagit internal] load build context
#15 transferring context: 68B done
#15 DONE 0.0s

#16 [dagster-daemon internal] load build context
#16 transferring context: 68B done
#16 DONE 0.0s

#17 [dagit runner 1/4] RUN groupadd -r dagster && useradd -m -r -g dagster dagster
#17 CACHED

#18 [dagit runner 3/4] COPY --from=builder --chown=dagster /opt/dagster/dagster_home /opt/dagster/dagster_home
#18 CACHED

#19 [dagit builder 4/4] RUN pip install --no-cache-dir --upgrade pip==21.3.1 setuptools==60.2.0 wheel==0.37.1 &&     poetry config virtualenvs.path "/opt/venv" &&     poetry install --no-root --no-interaction --no-ansi --no-dev
#19 CACHED

#20 [dagit builder 3/4] COPY poetry.lock pyproject.toml /
#20 CACHED

#21 [dagit builder 1/4] RUN python -m venv "/opt/venv" &&     mkdir -p "/opt/dagster/dagster_home"
#21 CACHED

#22 [dagit builder 2/4] RUN apt-get update &&     apt-get -y upgrade &&     apt-get install -y --no-install-recommends         curl         build-essential         libpq-dev &&     apt-get -y clean &&     rm -rf /var/lib/apt/lists/* &&     curl -sSL https://install.python-poetry.org | python -
#22 CACHED

#23 [dagit runner 2/4] COPY --from=builder /opt/venv /opt/venv
#23 CACHED

#24 [dagit runner 4/4] WORKDIR /opt/dagster/dagster_home
#24 CACHED

#25 [challenge builder 1/4] RUN python -m venv "/opt/venv" &&     mkdir -p "/opt/dagster/dagster_home"
#25 CACHED

#26 [challenge builder 2/4] RUN apt-get update &&     apt-get -y upgrade &&     apt-get install -y --no-install-recommends         curl         build-essential         libpq-dev &&     apt-get -y clean &&     rm -rf /var/lib/apt/lists/* &&     curl -sSL https://install.python-poetry.org | python -
#26 CACHED

#27 [challenge runner 2/4] COPY --from=builder /opt/venv /opt/venv
#27 CACHED

#28 [challenge builder 3/4] COPY poetry.lock pyproject.toml /
#28 CACHED

#29 [challenge runner 3/4] COPY --from=builder --chown=dagster /opt/dagster/dagster_home /opt/dagster/dagster_home
#29 CACHED

#30 [challenge builder 4/4] RUN pip install --no-cache-dir --upgrade pip==21.3.1 setuptools==60.2.0 wheel==0.37.1 &&     poetry config virtualenvs.path "/opt/venv" &&     poetry install --no-root --no-interaction --no-ansi --no-dev
#30 CACHED

#31 [challenge runner 4/4] WORKDIR /opt/dagster/dagster_home
#31 CACHED

#32 [challenge runner 1/4] RUN groupadd -r dagster && useradd -m -r -g dagster dagster
#32 CACHED

#33 [challenge challenge 1/1] COPY week_2/workspaces/ ./workspaces
#33 CACHED

#34 [project internal] load build context
#34 transferring context: 1.70kB done
#34 DONE 0.0s

#35 [content] exporting to image
#35 exporting layers done
#35 writing image sha256:c96f29c7845449a2ded4fba8f399904c7c36b9433cd0f366d248286fc9adb9d0 done
#35 naming to docker.io/library/corise-dagster-content done
#35 DONE 0.0s

#36 [challenge] exporting to image
#36 exporting layers done
#36 writing image sha256:15048a08dfba6a028a06d44cc9d2850f328a01d770b78d666f05c0502bf61a3d done
#36 naming to docker.io/library/corise-dagster-challenge done
#36 DONE 0.0s

#37 [dagit] exporting to image
#37 exporting layers done
#37 writing image sha256:5855bc53317e9f80f3da08db3a4091c9fb9cd336b91aec318d950fe14c87ee4a done
#37 naming to docker.io/library/corise-dagster-dagit done
#37 DONE 0.0s

#38 [dagster-daemon] exporting to image
#38 exporting layers done
#38 writing image sha256:37810501cebe527af9091b8e5882772d5d1e2177fecdb44066b1a91d58777df9 done
#38 naming to docker.io/library/corise-dagster-dagster-daemon done
#38 DONE 0.0s

#39 [project] exporting to image
#39 exporting layers done
#39 writing image sha256:c0ed4db39d4c2a50930277d2fcc80e2cfeaadcf83699e663f9cd817075677a0f done
#39 naming to docker.io/library/corise-dagster-project done
#39 DONE 0.0s
