package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.characters.*;
import com.fs.starfarer.api.util.Misc;
import org.lwjgl.util.vector.Vector2f;

import com.fs.starfarer.api.characters.LevelBasedEffect.ScopeDescription;
import com.fs.starfarer.api.combat.CombatEntityAPI;
import com.fs.starfarer.api.combat.DamageAPI;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.combat.listeners.AdvanceableListener;
import com.fs.starfarer.api.combat.listeners.DamageTakenModifier;
import com.fs.starfarer.api.impl.campaign.ids.Stats;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.impl.campaign.skills.DamageControl.DamageControlDamageTakenMod;
import com.fs.starfarer.api.ui.TooltipMakerAPI;

public class CaptainsDamageControl {
	
	public static boolean loadStock = false;
	
	public static float NO_OFFICER_MULT = 0.5f;
//	public static float INSTA_REPAIR = 0.25f;
//	public static int INSTA_REPAIR_PERC = 25;
	public static float CREW_LOSS_REDUCTION = 35; //In concert with containment procedures
	public static float COMPONENT_REPAIR_BONUS = 75;
	public static float COMPONENT_DAMAGE_TAKEN = 50f;
	public static float HULL_DAMAGE_REDUCTION = 25;

	public static boolean USE_HIT_NULL = false;
	public static float HIT_NULL_COOLDOWN = 3600;
	public static float HIT_NULL_MIN = 1000;
	public static float HIT_NULL_PERC = 75;

	public static class Level1 implements ShipSkillEffect {
			
			public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
				stats.getDynamic().getMod(Stats.INDIVIDUAL_SHIP_RECOVERY_MOD).modifyFlat(id, 1000f);
			}
			
			public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
				stats.getDynamic().getMod(Stats.INDIVIDUAL_SHIP_RECOVERY_MOD).unmodify(id);
			}
			
			public String getEffectDescription(float level) {
				return "如果该舰在战斗中被击沉，将几乎总是可在战后被打捞并修复。";
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
			stats.getCrewLossMult().modifyMult(id, 1f - CREW_LOSS_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getCrewLossMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + Math.round(CREW_LOSS_REDUCTION) + "% 战斗中因船体结构受损而造成的船员伤亡";
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
			float timeMult = 1f / ((100f + COMPONENT_REPAIR_BONUS) / 100f);
			stats.getCombatWeaponRepairTimeMult().modifyMult(id, timeMult);
			stats.getCombatEngineRepairTimeMult().modifyMult(id, timeMult);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getCombatWeaponRepairTimeMult().unmodify(id);
			stats.getCombatEngineRepairTimeMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + Math.round(COMPONENT_REPAIR_BONUS) + "% 武器和引擎战时修复速度";
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
			stats.getHullDamageTakenMult().modifyMult(id, 1f - HULL_DAMAGE_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getHullDamageTakenMult().unmodify(id);
		}	
		
		public String getEffectDescription(float level) {
			return "-" + Math.round(HULL_DAMAGE_REDUCTION) + "% 船体结构受到的伤害";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
//	public static class Level5 implements ShipSkillEffect {
//		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
//			stats.getDynamic().getMod(Stats.INSTA_REPAIR_FRACTION).modifyFlat(id, (float)(INSTA_REPAIR_PERC / 100f));
//		}
//		
//		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
//			stats.getDynamic().getMod(Stats.INSTA_REPAIR_FRACTION).unmodify(id);
//		}	
//		
//		public String getEffectDescription(float level) {
//			return "" + Math.round(INSTA_REPAIR_PERC) + "% of hull and armor damage automatically repaired for piloted ship after combat ends, at no cost";
//		}
//		
//		public String getEffectPerLevelDescription() {
//			return null;
//		}
//		
//		public ScopeDescription getScopeDescription() {
//			return ScopeDescription.PILOTED_SHIP;
//		}
//	}
	
	public static class Level7 implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getEngineDamageTakenMult().modifyMult(id, 1f - COMPONENT_DAMAGE_TAKEN / 100f);
			stats.getWeaponDamageTakenMult().modifyMult(id, 1f - COMPONENT_DAMAGE_TAKEN / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getEngineDamageTakenMult().unmodify(id);
			stats.getWeaponDamageTakenMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(COMPONENT_DAMAGE_TAKEN) + "% 武器和引擎受到的伤害";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level7B implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getEngineDamageTakenMult().modifyMult(id, 1f - COMPONENT_DAMAGE_TAKEN / 100f);
			stats.getWeaponDamageTakenMult().modifyMult(id, 1f - COMPONENT_DAMAGE_TAKEN / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getEngineDamageTakenMult().unmodify(id);
			stats.getWeaponDamageTakenMult().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "-" + (int)(COMPONENT_DAMAGE_TAKEN * NO_OFFICER_MULT) + "% 武器和引擎受到的伤害";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level6 extends BaseSkillEffectDescription implements AfterShipCreationSkillEffect {
		public void applyEffectsAfterShipCreation(ShipAPI ship, String id) {
			if (USE_HIT_NULL) { ship.addListener(new DamageControlDamageTakenMod(ship)); }
		}

		public void unapplyEffectsAfterShipCreation(ShipAPI ship, String id) {
			if (USE_HIT_NULL) { ship.removeListenerOfClass(DamageControlDamageTakenMod.class); }
		}
		
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {}
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {}
		
		public String getEffectDescription(float level) {
			return null;
		}
		
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
											TooltipMakerAPI info, float width) {
			init(stats, skill);

			Color c = hc;
			float level = stats.getSkillLevel(skill.getId());
			if (level < 2) {
				c = dhc;
			}
			String seconds = "" + (int) HIT_NULL_COOLDOWN + " 秒";
			if (HIT_NULL_COOLDOWN == 1f) seconds = "秒";
			//info.addPara("Single-hit hull damage above %s points has the portion above %s reduced by %s",
			if (USE_HIT_NULL) {
				info.addPara("每 " +  seconds + " 最多触发一次，当船体结构受到一次超过 %s 点的伤害时，其超过 %s 点的部分将降低 %s",
					0f, c, c,
					"" + (int) HIT_NULL_MIN,
					"" + (int) HIT_NULL_MIN,
					"" + (int) HIT_NULL_PERC + "%"
				);
			}
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	
	public static class DamageControlDamageTakenMod implements DamageTakenModifier, AdvanceableListener {
		protected ShipAPI ship;
		protected float sinceProc = HIT_NULL_COOLDOWN + 1f;
		public DamageControlDamageTakenMod(ShipAPI ship) {
			this.ship = ship;
		}
		
		public void advance(float amount) {
			sinceProc += amount;
		}
		
		public String modifyDamageTaken(Object param, CombatEntityAPI target, 
										DamageAPI damage, Vector2f point,
										boolean shieldHit) {
			if (!shieldHit && sinceProc > HIT_NULL_COOLDOWN) {
				float mult = 1f - HIT_NULL_PERC / 100f;
				ship.setNextHitHullDamageThresholdMult(HIT_NULL_MIN, mult);
				sinceProc = 0f;
			}
			return null;
		}
	}

	public static class Level8Desc implements DescriptionSkillEffect {
		public String getString() {
			return "\n\n*通常而言，受损但未下线的武器和引擎将在不受到火力伤害 5 秒后才开始维修。";
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			h = Misc.getDarkHighlightColor();
			return new Color[] {h};
		}
		public String[] getHighlights() {
			return new String [] {"5"};
		}
		public Color getTextColor() {
			return null;
		}
	}
	public static class Level8 implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getDynamic().getMod(Stats.CAN_REPAIR_MODULES_UNDER_FIRE).modifyFlat(id, 1f);
		}

		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.CAN_REPAIR_MODULES_UNDER_FIRE).unmodifyFlat(id);
		}

		public String getEffectDescription(float level) {
			return "即使正受到持续火力*，也能持续修复受损但未下线的武器和引擎。";
		}

		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
}
