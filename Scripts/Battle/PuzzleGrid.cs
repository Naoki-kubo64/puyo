using UnityEngine;
using System.Collections.Generic;

public class PuzzleGrid : MonoBehaviour
{
    [Header("Grid Settings")]
    public GameConfig config;
    public Transform gridParent;
    public GameObject puyoPrefab;
    
    private PuyoData[,] grid;
    private Vector3 gridOrigin;
    
    public int Width => config.gridWidth;
    public int Height => config.gridHeight;
    
    void Awake()
    {
        InitializeGrid();
    }
    
    void InitializeGrid()
    {
        grid = new PuyoData[Width, Height];
        gridOrigin = transform.position;
        
        for (int x = 0; x < Width; x++)
        {
            for (int y = 0; y < Height; y++)
            {
                grid[x, y] = new PuyoData(PuyoColor.Empty, new Vector2Int(x, y));
            }
        }
    }
    
    public Vector3 GridToWorldPosition(Vector2Int gridPos)
    {
        return gridOrigin + new Vector3(gridPos.x * config.cellSize, gridPos.y * config.cellSize, 0);
    }
    
    public Vector2Int WorldToGridPosition(Vector3 worldPos)
    {
        Vector3 localPos = worldPos - gridOrigin;
        return new Vector2Int(
            Mathf.FloorToInt(localPos.x / config.cellSize),
            Mathf.FloorToInt(localPos.y / config.cellSize)
        );
    }
    
    public bool IsValidPosition(Vector2Int pos)
    {
        return pos.x >= 0 && pos.x < Width && pos.y >= 0 && pos.y < Height;
    }
    
    public bool IsPositionEmpty(Vector2Int pos)
    {
        if (!IsValidPosition(pos)) return false;
        return grid[pos.x, pos.y].IsEmpty;
    }
    
    public PuyoData GetPuyo(Vector2Int pos)
    {
        if (!IsValidPosition(pos)) return null;
        return grid[pos.x, pos.y];
    }
    
    public void SetPuyo(Vector2Int pos, PuyoData puyo)
    {
        if (!IsValidPosition(pos)) return;
        grid[pos.x, pos.y] = puyo;
        puyo.gridPosition = pos;
    }
    
    public void RemovePuyo(Vector2Int pos)
    {
        if (!IsValidPosition(pos)) return;
        
        PuyoData puyo = grid[pos.x, pos.y];
        if (puyo.gameObject != null)
        {
            Destroy(puyo.gameObject);
        }
        
        grid[pos.x, pos.y] = new PuyoData(PuyoColor.Empty, pos);
    }
    
    public GameObject CreatePuyoGameObject(PuyoColor color, Vector2Int gridPos)
    {
        GameObject puyoObj = Instantiate(puyoPrefab, gridParent);
        puyoObj.transform.position = GridToWorldPosition(gridPos);
        
        Renderer renderer = puyoObj.GetComponent<Renderer>();
        if (renderer != null)
        {
            Material puyoMaterial = GetPuyoMaterial(color);
            if (puyoMaterial != null)
            {
                renderer.material = puyoMaterial;
            }
            else
            {
                // Fallback to color if no material found
                Material newMat = new Material(renderer.material);
                newMat.color = GetPuyoColor(color);
                renderer.material = newMat;
            }
        }
        
        return puyoObj;
    }
    
    private Material GetPuyoMaterial(PuyoColor color)
    {
        string materialPath = "";
        switch (color)
        {
            case PuyoColor.Red: materialPath = "Assets/Materials/PuyoRed.mat"; break;
            case PuyoColor.Blue: materialPath = "Assets/Materials/PuyoBlue.mat"; break;
            case PuyoColor.Green: materialPath = "Assets/Materials/PuyoGreen.mat"; break;
            case PuyoColor.Yellow: materialPath = "Assets/Materials/PuyoYellow.mat"; break;
            case PuyoColor.Purple: materialPath = "Assets/Materials/PuyoPurple.mat"; break;
            default: return null;
        }
        
#if UNITY_EDITOR
        return UnityEditor.AssetDatabase.LoadAssetAtPath<Material>(materialPath);
#else
        return Resources.Load<Material>(materialPath);
#endif
    }
    
    private Color GetPuyoColor(PuyoColor color)
    {
        switch (color)
        {
            case PuyoColor.Red: return Color.red;
            case PuyoColor.Blue: return Color.blue;
            case PuyoColor.Green: return Color.green;
            case PuyoColor.Yellow: return Color.yellow;
            case PuyoColor.Purple: return Color.magenta;
            default: return Color.white;
        }
    }
    
    public List<Vector2Int> GetConnectedPuyos(Vector2Int startPos, PuyoColor targetColor)
    {
        List<Vector2Int> connected = new List<Vector2Int>();
        bool[,] visited = new bool[Width, Height];
        
        FloodFill(startPos, targetColor, connected, visited);
        
        return connected;
    }
    
    private void FloodFill(Vector2Int pos, PuyoColor targetColor, List<Vector2Int> connected, bool[,] visited)
    {
        if (!IsValidPosition(pos) || visited[pos.x, pos.y]) return;
        
        PuyoData puyo = GetPuyo(pos);
        if (puyo.color != targetColor || puyo.IsEmpty) return;
        
        visited[pos.x, pos.y] = true;
        connected.Add(pos);
        
        Vector2Int[] directions = {
            Vector2Int.up, Vector2Int.down, Vector2Int.left, Vector2Int.right
        };
        
        foreach (Vector2Int dir in directions)
        {
            FloodFill(pos + dir, targetColor, connected, visited);
        }
    }
}