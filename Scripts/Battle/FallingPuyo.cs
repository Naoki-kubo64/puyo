using UnityEngine;

public class FallingPuyo : MonoBehaviour
{
    [Header("Components")]
    public PuyoData puyoData1;
    public PuyoData puyoData2;
    public GameObject puyo1Object;
    public GameObject puyo2Object;
    
    private PuzzleGrid grid;
    private GameConfig config;
    private Vector2Int currentPosition;
    private int rotation = 0;
    private float fallTimer = 0f;
    private bool isControlled = true;
    
    public Vector2Int Position => currentPosition;
    public bool IsControlled => isControlled;
    
    void Start()
    {
        grid = FindFirstObjectByType<PuzzleGrid>();
        config = grid.config;
        
        currentPosition = new Vector2Int(grid.Width / 2, grid.Height - 1);
        UpdateVisualPosition();
    }
    
    void Update()
    {
        if (!isControlled) return;
        
        HandleInput();
        HandleFalling();
    }
    
    void HandleInput()
    {
        if (Input.GetKeyDown(KeyCode.LeftArrow))
        {
            TryMove(Vector2Int.left);
        }
        else if (Input.GetKeyDown(KeyCode.RightArrow))
        {
            TryMove(Vector2Int.right);
        }
        else if (Input.GetKeyDown(KeyCode.UpArrow))
        {
            TryRotate();
        }
        
        if (Input.GetKey(KeyCode.DownArrow))
        {
            fallTimer += Time.deltaTime * config.fastFallMultiplier;
        }
    }
    
    void HandleFalling()
    {
        fallTimer += Time.deltaTime;
        
        if (fallTimer >= 1f / config.fallSpeed)
        {
            if (!TryMove(Vector2Int.down))
            {
                LandPuyo();
            }
            fallTimer = 0f;
        }
    }
    
    bool TryMove(Vector2Int direction)
    {
        Vector2Int newPos = currentPosition + direction;
        Vector2Int puyo1Pos = GetPuyo1Position(newPos, rotation);
        Vector2Int puyo2Pos = GetPuyo2Position(newPos, rotation);
        
        if (CanMoveTo(puyo1Pos) && CanMoveTo(puyo2Pos))
        {
            currentPosition = newPos;
            UpdateVisualPosition();
            return true;
        }
        
        return false;
    }
    
    bool TryRotate()
    {
        int newRotation = (rotation + 1) % 4;
        Vector2Int puyo1Pos = GetPuyo1Position(currentPosition, newRotation);
        Vector2Int puyo2Pos = GetPuyo2Position(currentPosition, newRotation);
        
        if (CanMoveTo(puyo1Pos) && CanMoveTo(puyo2Pos))
        {
            rotation = newRotation;
            UpdateVisualPosition();
            return true;
        }
        
        Vector2Int[] kickPositions = { Vector2Int.left, Vector2Int.right };
        foreach (Vector2Int kick in kickPositions)
        {
            Vector2Int kickedPos = currentPosition + kick;
            puyo1Pos = GetPuyo1Position(kickedPos, newRotation);
            puyo2Pos = GetPuyo2Position(kickedPos, newRotation);
            
            if (CanMoveTo(puyo1Pos) && CanMoveTo(puyo2Pos))
            {
                currentPosition = kickedPos;
                rotation = newRotation;
                UpdateVisualPosition();
                return true;
            }
        }
        
        return false;
    }
    
    bool CanMoveTo(Vector2Int pos)
    {
        if (!grid.IsValidPosition(pos)) return false;
        if (pos.y < 0) return false;
        return grid.IsPositionEmpty(pos);
    }
    
    Vector2Int GetPuyo1Position(Vector2Int basePos, int rot)
    {
        return basePos;
    }
    
    Vector2Int GetPuyo2Position(Vector2Int basePos, int rot)
    {
        Vector2Int[] offsets = {
            Vector2Int.up,
            Vector2Int.right,
            Vector2Int.down,
            Vector2Int.left
        };
        
        return basePos + offsets[rot];
    }
    
    void UpdateVisualPosition()
    {
        Vector2Int puyo1Pos = GetPuyo1Position(currentPosition, rotation);
        Vector2Int puyo2Pos = GetPuyo2Position(currentPosition, rotation);
        
        puyo1Object.transform.position = grid.GridToWorldPosition(puyo1Pos);
        puyo2Object.transform.position = grid.GridToWorldPosition(puyo2Pos);
    }
    
    void LandPuyo()
    {
        Vector2Int puyo1Pos = GetPuyo1Position(currentPosition, rotation);
        Vector2Int puyo2Pos = GetPuyo2Position(currentPosition, rotation);
        
        puyoData1.gameObject = puyo1Object;
        puyoData1.state = PuyoState.Landed;
        grid.SetPuyo(puyo1Pos, puyoData1);
        
        puyoData2.gameObject = puyo2Object;
        puyoData2.state = PuyoState.Landed;
        grid.SetPuyo(puyo2Pos, puyoData2);
        
        isControlled = false;
        
        PuzzleManager puzzleManager = FindFirstObjectByType<PuzzleManager>();
        if (puzzleManager != null)
        {
            puzzleManager.OnPuyoLanded();
        }
        
        Destroy(this);
    }
    
    public void Initialize(PuyoColor color1, PuyoColor color2)
    {
        puyoData1 = new PuyoData(color1, Vector2Int.zero);
        puyoData2 = new PuyoData(color2, Vector2Int.zero);
        
        puyo1Object = grid.CreatePuyoGameObject(color1, Vector2Int.zero);
        puyo2Object = grid.CreatePuyoGameObject(color2, Vector2Int.zero);
        
        puyo1Object.transform.SetParent(transform);
        puyo2Object.transform.SetParent(transform);
    }
}