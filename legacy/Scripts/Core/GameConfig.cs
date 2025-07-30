using UnityEngine;

[CreateAssetMenu(fileName = "GameConfig", menuName = "Puyo Rogue/Game Config")]
public class GameConfig : ScriptableObject
{
    [Header("Grid Settings")]
    public int gridWidth = 6;
    public int gridHeight = 12;
    public float cellSize = 1f;
    
    [Header("Puyo Physics")]
    public float fallSpeed = 2f;
    public float fastFallMultiplier = 5f;
    
    [Header("Chain Settings")]
    public int minimumChainLength = 4;
    public float chainDelay = 0.3f;
    public float baseDamage = 10f;
    public float chainMultiplier = 1.5f;
    
    [Header("Enemy Settings")]
    public float enemyAttackInterval = 3f;
    public int enemyBaseDamage = 15;
    
    [Header("Player Settings")]
    public int playerMaxHP = 100;
    public int playerStartHP = 100;
}