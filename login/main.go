package main

import (
	"fmt"
	"golang.org/x/text/encoding/simplifiedchinese"
	"golang.org/x/text/transform"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"
)

const (
	host = "202.204.48.66"
)

var (
	username = ""
	password = ""
)

func getV6IP() string {
	resp, err := http.Get("http://cippv6.ustb.edu.cn/get_ip.php")
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	text := string(body)
	return text[strings.IndexAny(text, "'")+1 : strings.LastIndexAny(text, "'")]

}
func login() (bool, bool) {
	form := url.Values{}
	form.Set("DDDDD", username)
	form.Set("upass", password)
	form.Set("0MKKey", "123456")
	ipv6 := getV6IP()
	form.Set("v6ip", ipv6)
	resp, err := http.PostForm("http://"+host, form)
	if err != nil {
		log.Println(err)
		return false, ipv6 != ""
	}
	defer resp.Body.Close()
	utf8Reader := transform.NewReader(resp.Body, simplifiedchinese.GBK.NewDecoder())
	body, _ := ioutil.ReadAll(utf8Reader)
	text := string(body)
	if ipv6 != "" {
		fmt.Println(ipv6)
	}
	if strings.Contains(text, "认证成功") || strings.Contains(text, "uid='") || strings.Contains(text, "文法学院机房专线'") {
		return true, ipv6 != ""
	}
	fmt.Println("\n" + text)

	return false, ipv6 != ""
}
func isLogin() bool {
	resp, err := http.Get("http://" + host)
	if err != nil {
		log.Println(err)
		return true
	}
	//程序在使用完回复后必须关闭回复的主体。
	defer resp.Body.Close()
	utf8Reader := transform.NewReader(resp.Body, simplifiedchinese.GBK.NewDecoder())
	body, _ := ioutil.ReadAll(utf8Reader)
	text := string(body)
	if strings.Contains(text, "uid='") {
		return true
	}
	return false
}
func main() {
	flag := true
	n := 0
	fmt.Println("start")
	for {
		if !isLogin() {
			success, v6 := login()
			if !success {
				fmt.Print("\rlogin fail", n)
				if !flag {
					n += 1
					if n > 5 {
						time.Sleep(3 * time.Minute)
					}
					if n > 10 {
						panic("fail too many times")
					}
				}
				flag = false
			} else {
				flag = true
				n = 0
				fmt.Print("\rlogin success. ipv6:", v6)
			}
		}
		time.Sleep(30 + time.Second)
	}
}
