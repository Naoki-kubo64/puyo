using UnityEngine;

public enum PuyoColor
{
    Red,
    Blue,
    Green,
    Yellow,
    Purple,
    Empty
}

public enum PuyoState
{
    Falling,
    Landed,
    Matched,
    Destroyed
}

[System.Serializable]
public class PuyoData
{
    public PuyoColor color;
    public PuyoState state;
    public Vector2Int gridPosition;
    public GameObject gameObject;
    
    public PuyoData(PuyoColor color, Vector2Int position)
    {
        this.color = color;
        this.gridPosition = position;
        this.state = PuyoState.Falling;
    }
    
    public bool IsEmpty => color == PuyoColor.Empty;
    public bool CanMatch => state == PuyoState.Landed && !IsEmpty;
}