package dal.impl.campaign.skills;

import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

public class CaptainsFieldModulation {
	
	public static boolean loadStock = false;
	public static float SHIELD_DAMAGE_REDUCTION = 15f;
	public static float FLUX_SHUNT_DISSIPATION = 15f;
	public static float SHIELD_RATE_BONUS = 25f;
	public static float PHASE_FLUX_UPKEEP_REDUCTION = 25f;
	public static float PHASE_COOLDOWN_REDUCTION = 35f;
	public static float PHASE_FLUX_THRESHOLD_BONUS = 25f;


	public static class Level1 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getShieldDamageTakenMult().modifyMult(id, 1f - SHIELD_DAMAGE_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getShieldDamageTakenMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(SHIELD_DAMAGE_REDUCTION) + "% 护盾所受伤害";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level2 implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getPhaseCloakUpkeepCostBonus().modifyMult(id, 1f - PHASE_FLUX_UPKEEP_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getPhaseCloakUpkeepCostBonus().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(PHASE_FLUX_UPKEEP_REDUCTION) + "% 激活相位隐形所产生的幅能";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level3 implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getHardFluxDissipationFraction().modifyFlat(id, FLUX_SHUNT_DISSIPATION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getHardFluxDissipationFraction().unmodify(id);
		}	
		
		public String getEffectDescription(float level) {
			return "即便护盾处于激活状态，也能以 " + (int)(FLUX_SHUNT_DISSIPATION) + "% 的速率耗散硬幅能";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level4 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getPhaseCloakCooldownBonus().modifyMult(id, 1f - PHASE_COOLDOWN_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getPhaseCloakCooldownBonus().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(PHASE_COOLDOWN_REDUCTION) + "% 相位隐形的冷却时间";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level5 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getShieldUnfoldRateMult().modifyMult(id, 1f + (SHIELD_RATE_BONUS / 100f));
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getShieldUnfoldRateMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(SHIELD_RATE_BONUS) + "% 护盾展开速度";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
}
