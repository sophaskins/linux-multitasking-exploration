package main

import (
	"bytes"
	"flag"
	"github.com/ulikunitz/xz"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"time"
)

// setupZippedReader fetches our zipped workload from the internet
func setupZippedReader(url string) (io.ReadSeeker, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}

	log.Println("Beginning download of " + url)

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	zippedReader := bytes.NewReader(body)

	log.Println("Finished download of " + url)

	return zippedReader, nil
}

func main() {
	zippedURL := flag.String("url", "https://large-tarballs.sophaskins.net/kernel.tar.gz", "the url of a large tarball to download")
	sleepHowOften := flag.Int("freq", 100, "how often the task should sleep")
	sleepHowLong := flag.Int("duration", 50, "how long to sleep")
	flag.Parse()

	// When there's a message on this channel, we should sleep for sleepHowLong ms
	shouldSleepChan := time.Tick(time.Duration(*sleepHowOften) * time.Millisecond)

	zippedReader, err := setupZippedReader(*zippedURL)
	if err != nil {
		log.Fatal(err)
	}

	for {
		// For each pass through the file, we need to re-wind the reader and
		// re-setup the xzReader (otherwise we'd hit the EOF immediately!)
		zippedReader.Seek(0, 0)
		xzReader, err := xz.NewReader(zippedReader)
		if err != nil {
			log.Fatal(err)
		}

		// our "work" is reading the xz file in to a buffer 1024 bytes at a time.
		buffer := make([]byte, 1024)

		err = nil
		for err == nil {
			select {
			case _ = <-shouldSleepChan:
				time.Sleep(time.Duration(*sleepHowLong) * time.Millisecond)
			default:
				_, err = xzReader.Read(buffer)
			}
		}

		// If we've made it to the end, err will be io.EOF (and
		// thus we should loop through the file again!) Otherwise,
		// something is seriously wrong
		if err != nil && err != io.EOF {
			log.Fatal(err)
		}
	}
}
