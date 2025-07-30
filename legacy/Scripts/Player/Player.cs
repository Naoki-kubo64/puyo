using UnityEngine;

public class Player : MonoBehaviour
{
    [Header("Stats")]
    public int maxHP;
    public int currentHP;
    
    [Header("Events")]
    public System.Action<int, int> OnHealthChanged;
    public System.Action OnPlayerDied;
    
    void Start()
    {
        if (maxHP <= 0) maxHP = 100;
        currentHP = maxHP;
        OnHealthChanged?.Invoke(currentHP, maxHP);
    }
    
    public void TakeDamage(int damage)
    {
        currentHP = Mathf.Max(0, currentHP - damage);
        OnHealthChanged?.Invoke(currentHP, maxHP);
        
        Debug.Log($"Player took {damage} damage. HP: {currentHP}/{maxHP}");
        
        if (currentHP <= 0)
        {
            OnPlayerDied?.Invoke();
        }
    }
    
    public void Heal(int amount)
    {
        currentHP = Mathf.Min(maxHP, currentHP + amount);
        OnHealthChanged?.Invoke(currentHP, maxHP);
        
        Debug.Log($"Player healed {amount} HP. HP: {currentHP}/{maxHP}");
    }
    
    public void SetMaxHP(int newMaxHP)
    {
        float healthPercentage = (float)currentHP / maxHP;
        maxHP = newMaxHP;
        currentHP = Mathf.RoundToInt(maxHP * healthPercentage);
        OnHealthChanged?.Invoke(currentHP, maxHP);
    }
    
    public bool IsAlive => currentHP > 0;
    public float HealthPercentage => (float)currentHP / maxHP;
}