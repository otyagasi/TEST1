package main

import (
	"errors"
	// "fmt"
	// "go.uber.org/multierr"
)

func step1() error {
	return errors.New("failed to execute step1")
}

func step2() error {
	return errors.New("failed to execute step2")
}

// func main() {
// 	var rerr error

// 	// step1の実行とエラーの確認
// 	if err := step1(); err != nil {
// 		rerr = multierr.Append(rerr, err)
// 	}

// 	if err := step2(); err != nil {
// 		rerr = multierr.Append(rerr, err)
// 	}

// 	//まとめたエラーを出力
// 	if rerr != nil {
// 		fmt.Printf("Errors encountered:%v \n", rerr)
// 	} else {
// 		fmt.Println("No errors encountered.")
// 	}
// }