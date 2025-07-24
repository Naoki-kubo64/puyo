using UnityEngine;
using System.Collections;

public class Enemy : MonoBehaviour
{
    [Header("Stats")]
    public int maxHP = 100;
    public int currentHP;
    public int attackDamage = 15;
    public float attackInterval = 3f;
    
    [Header("Visual")]
    public SpriteRenderer spriteRenderer;
    public string enemyName = "Slime";
    
    [Header("Events")]
    public System.Action<int, int> OnHealthChanged;
    public System.Action OnEnemyDied;
    public System.Action<int> OnAttack;
    
    private float attackTimer;
    private bool isAlive = true;
    private bool battleActive = true;
    
    public float AttackTimeRemaining => Mathf.Max(0, attackInterval - attackTimer);
    public bool IsAlive => isAlive;
    public string Name => enemyName;
    
    void Start()
    {
        currentHP = maxHP;
        attackTimer = 0f;
        OnHealthChanged?.Invoke(currentHP, maxHP);
    }
    
    void Update()
    {
        if (!isAlive || !battleActive) return;
        
        attackTimer += Time.deltaTime;
        
        if (attackTimer >= attackInterval)
        {
            PerformAttack();
            attackTimer = 0f;
        }
    }
    
    public void TakeDamage(int damage)
    {
        if (!isAlive) return;
        
        currentHP = Mathf.Max(0, currentHP - damage);
        OnHealthChanged?.Invoke(currentHP, maxHP);
        
        Debug.Log($"{enemyName} took {damage} damage. HP: {currentHP}/{maxHP}");
        
        StartCoroutine(DamageFlash());
        
        if (currentHP <= 0)
        {
            Die();
        }
    }
    
    private IEnumerator DamageFlash()
    {
        if (spriteRenderer != null)
        {
            Color originalColor = spriteRenderer.color;
            spriteRenderer.color = Color.red;
            yield return new WaitForSeconds(0.1f);
            spriteRenderer.color = originalColor;
        }
    }
    
    private void PerformAttack()
    {
        if (!isAlive) return;
        
        Debug.Log($"{enemyName} attacks for {attackDamage} damage!");
        OnAttack?.Invoke(attackDamage);
        
        StartCoroutine(AttackAnimation());
    }
    
    private IEnumerator AttackAnimation()
    {
        if (spriteRenderer != null)
        {
            Vector3 originalScale = transform.localScale;
            
            transform.localScale = originalScale * 1.2f;
            yield return new WaitForSeconds(0.1f);
            transform.localScale = originalScale;
        }
    }
    
    private void Die()
    {
        isAlive = false;
        Debug.Log($"{enemyName} has been defeated!");
        
        OnEnemyDied?.Invoke();
        
        StartCoroutine(DeathAnimation());
    }
    
    private IEnumerator DeathAnimation()
    {
        if (spriteRenderer != null)
        {
            float duration = 0.5f;
            float elapsed = 0f;
            Color startColor = spriteRenderer.color;
            
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float alpha = 1f - (elapsed / duration);
                spriteRenderer.color = new Color(startColor.r, startColor.g, startColor.b, alpha);
                yield return null;
            }
        }
        
        gameObject.SetActive(false);
    }
    
    public void SetBattleActive(bool active)
    {
        battleActive = active;
    }
    
    public void ResetAttackTimer()
    {
        attackTimer = 0f;
    }
    
    public void ModifyAttackInterval(float modifier)
    {
        attackInterval *= modifier;
        attackInterval = Mathf.Max(0.5f, attackInterval);
    }
    
    public void SetStats(int hp, int damage, float interval, string name)
    {
        maxHP = hp;
        currentHP = hp;
        attackDamage = damage;
        attackInterval = interval;
        enemyName = name;
        
        OnHealthChanged?.Invoke(currentHP, maxHP);
    }
    
    public float HealthPercentage => (float)currentHP / maxHP;
}