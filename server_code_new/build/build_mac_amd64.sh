docker run --rm -v $PWD/../:/build -e CGO_ENABLED=0 -e GOOS=darwin -e GOARCH=amd64 -w /build golang:1.18-alpine go build -trimpath --ldflags "-w -s" -o data_collector .
