using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class PuzzleManager : MonoBehaviour
{
    [Header("References")]
    public PuzzleGrid grid;
    public GameObject fallingPuyoPrefab;
    public GameConfig config;
    
    private FallingPuyo currentFallingPuyo;
    private bool isProcessingChains = false;
    private bool gameActive = true;
    
    public System.Action<int, int> OnChainCompleted;
    
    void Start()
    {
        if (gameActive)
        {
            SpawnNextPuyo();
        }
    }
    
    public void OnPuyoLanded()
    {
        if (!gameActive) return;
        
        StartCoroutine(ProcessChains());
    }
    
    void SpawnNextPuyo()
    {
        if (!gameActive || isProcessingChains) return;
        
        if (IsGameOver())
        {
            EndGame();
            return;
        }
        
        GameObject fallingPuyoObj = Instantiate(fallingPuyoPrefab, transform);
        currentFallingPuyo = fallingPuyoObj.GetComponent<FallingPuyo>();
        
        PuyoColor color1 = GetRandomPuyoColor();
        PuyoColor color2 = GetRandomPuyoColor();
        
        currentFallingPuyo.Initialize(color1, color2);
    }
    
    PuyoColor GetRandomPuyoColor()
    {
        PuyoColor[] colors = { PuyoColor.Red, PuyoColor.Blue, PuyoColor.Green, PuyoColor.Yellow, PuyoColor.Purple };
        return colors[Random.Range(0, colors.Length)];
    }
    
    bool IsGameOver()
    {
        Vector2Int spawnPos = new Vector2Int(grid.Width / 2, grid.Height - 1);
        Vector2Int topPos = spawnPos + Vector2Int.up;
        
        return !grid.IsPositionEmpty(spawnPos) || !grid.IsPositionEmpty(topPos);
    }
    
    void EndGame()
    {
        gameActive = false;
        Debug.Log("Game Over!");
        
        BattleManager battleManager = FindFirstObjectByType<BattleManager>();
        if (battleManager != null)
        {
            battleManager.OnPlayerDefeated();
        }
    }
    
    IEnumerator ProcessChains()
    {
        isProcessingChains = true;
        
        yield return StartCoroutine(ApplyGravity());
        
        int chainCount = 0;
        int totalCleared = 0;
        
        while (true)
        {
            List<Vector2Int> puyosToRemove = FindMatchingPuyos();
            
            if (puyosToRemove.Count == 0)
                break;
            
            chainCount++;
            totalCleared += puyosToRemove.Count;
            
            RemovePuyos(puyosToRemove);
            
            yield return new WaitForSeconds(config.chainDelay);
            
            yield return StartCoroutine(ApplyGravity());
        }
        
        if (chainCount > 0)
        {
            OnChainCompleted?.Invoke(chainCount, totalCleared);
        }
        
        isProcessingChains = false;
        SpawnNextPuyo();
    }
    
    List<Vector2Int> FindMatchingPuyos()
    {
        List<Vector2Int> toRemove = new List<Vector2Int>();
        bool[,] checked_ = new bool[grid.Width, grid.Height];
        
        for (int x = 0; x < grid.Width; x++)
        {
            for (int y = 0; y < grid.Height; y++)
            {
                if (checked_[x, y]) continue;
                
                Vector2Int pos = new Vector2Int(x, y);
                PuyoData puyo = grid.GetPuyo(pos);
                
                if (!puyo.CanMatch) continue;
                
                List<Vector2Int> connected = grid.GetConnectedPuyos(pos, puyo.color);
                
                foreach (Vector2Int connectedPos in connected)
                {
                    checked_[connectedPos.x, connectedPos.y] = true;
                }
                
                if (connected.Count >= config.minimumChainLength)
                {
                    toRemove.AddRange(connected);
                }
            }
        }
        
        return toRemove;
    }
    
    void RemovePuyos(List<Vector2Int> positions)
    {
        foreach (Vector2Int pos in positions)
        {
            grid.RemovePuyo(pos);
        }
    }
    
    IEnumerator ApplyGravity()
    {
        bool puyosFell = false;
        
        do
        {
            puyosFell = false;
            
            for (int x = 0; x < grid.Width; x++)
            {
                for (int y = 1; y < grid.Height; y++)
                {
                    PuyoData puyo = grid.GetPuyo(new Vector2Int(x, y));
                    if (puyo.IsEmpty) continue;
                    
                    Vector2Int belowPos = new Vector2Int(x, y - 1);
                    if (grid.IsPositionEmpty(belowPos))
                    {
                        grid.SetPuyo(belowPos, puyo);
                        grid.RemovePuyo(new Vector2Int(x, y));
                        
                        if (puyo.gameObject != null)
                        {
                            puyo.gameObject.transform.position = grid.GridToWorldPosition(belowPos);
                        }
                        
                        puyosFell = true;
                    }
                }
            }
            
            if (puyosFell)
            {
                yield return new WaitForSeconds(0.1f);
            }
            
        } while (puyosFell);
    }
    
    public void StopGame()
    {
        gameActive = false;
        if (currentFallingPuyo != null)
        {
            Destroy(currentFallingPuyo.gameObject);
        }
    }
    
    public void ResumeGame()
    {
        gameActive = true;
        if (currentFallingPuyo == null && !isProcessingChains)
        {
            SpawnNextPuyo();
        }
    }
}