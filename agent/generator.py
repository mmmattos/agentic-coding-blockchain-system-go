import os
import textwrap


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))


def generate_system(plan, base):
    # ------------------------
    # go.mod
    # ------------------------
    write(f"{base}/go.mod", """
    module blockchain

    go 1.21
    """)

    # ------------------------
    # main.go
    # ------------------------
    write(f"{base}/main.go", """
    package main

    import (
        "net/http"
        "os"
    )

    func main() {
        port := os.Getenv("PORT")
        if port == "" {
            port = "8001"
        }

        http.HandleFunc("/transaction", handleTransaction)
        http.HandleFunc("/mine", handleMine)
        http.HandleFunc("/chain", handleChain)
        http.HandleFunc("/sync", handleSync)

        http.ListenAndServe(":" + port, nil)
    }
    """)

    # ------------------------
    # blockchain.go (FIXED JSON TAGS)
    # ------------------------
    write(f"{base}/blockchain.go", """
    package main

    import (
        "crypto/sha256"
        "encoding/hex"
        "fmt"
        "time"
        "os"
    )

    type Transaction struct {
        ID     string  `json:"id"`
        Amount float64 `json:"amount"`
    }

    type Block struct {
        Index        int           `json:"index"`
        Timestamp    int64         `json:"timestamp"`
        Transactions []Transaction `json:"transactions"`
        PrevHash     string        `json:"prev_hash"`
        Hash         string        `json:"hash"`
    }

    type Blockchain struct {
        Blocks  []Block
        Pending []Transaction
    }

    func NewBlockchain() *Blockchain {
        bc := &Blockchain{}
        bc.Blocks = append(bc.Blocks, Block{
            Index:     0,
            Timestamp: time.Now().Unix(),
            PrevHash:  "0",
            Hash:      "genesis",
        })
        return bc
    }

    func (bc *Blockchain) AddTransaction(tx Transaction) {
        bc.Pending = append(bc.Pending, tx)
    }

    func (bc *Blockchain) MineBlock() {
        prev := bc.Blocks[len(bc.Blocks)-1]

        fake := os.Getenv("ADVERSARIAL") == "true"

        prevHash := prev.Hash
        if fake {
            prevHash = "fake_hash"
        }

        b := Block{
            Index:        len(bc.Blocks),
            Timestamp:    time.Now().Unix(),
            Transactions: bc.Pending,
            PrevHash:     prevHash,
        }

        b.Hash = hash(b)

        bc.Blocks = append(bc.Blocks, b)
        bc.Pending = nil
    }

    func (bc *Blockchain) ReplaceChain(newBlocks []Block) {
        if len(newBlocks) > len(bc.Blocks) {
            bc.Blocks = newBlocks
        }
    }

    func hash(b Block) string {
        s := fmt.Sprintf("%d%d%s", b.Index, b.Timestamp, b.PrevHash)
        h := sha256.Sum256([]byte(s))
        return hex.EncodeToString(h[:])
    }
    """)

    # ------------------------
    # handlers.go
    # ------------------------
    write(f"{base}/handlers.go", """
    package main

    import (
        "bytes"
        "encoding/json"
        "net/http"
    )

    var bc = NewBlockchain()

    var peers = []string{
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
    }

    func handleTransaction(w http.ResponseWriter, r *http.Request) {
        var tx Transaction
        json.NewDecoder(r.Body).Decode(&tx)
        bc.AddTransaction(tx)
    }

    func handleMine(w http.ResponseWriter, r *http.Request) {
        bc.MineBlock()
        go broadcast()
    }

    func handleChain(w http.ResponseWriter, r *http.Request) {
        json.NewEncoder(w).Encode(bc.Blocks)
    }

    func handleSync(w http.ResponseWriter, r *http.Request) {
        var chain []Block
        json.NewDecoder(r.Body).Decode(&chain)
        bc.ReplaceChain(chain)
    }

    func broadcast() {
        data, _ := json.Marshal(bc.Blocks)

        for _, peer := range peers {
            http.Post(peer+"/sync", "application/json", bytes.NewBuffer(data))
        }
    }
    """)