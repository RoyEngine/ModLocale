package dal.impl.campaign.skills;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.fleet.FleetMemberAPI;
import com.fs.starfarer.api.impl.campaign.ids.HullMods;
import com.fs.starfarer.api.impl.campaign.ids.Stats;

public class CaptainsSupportDoctrine {

	//Armada Doctrine
	
	public static boolean USE_HELM_BONUS = true;
	public static boolean USE_DAMCON_BONUS = true;
	public static boolean USE_ORDNANCE_BONUS = true;
	public static boolean USE_ENDURANCE_BONUS = false;
	public static String SUPPORT_DOCTRINE_DP_REDUCTION_ID = "support_doctrine_dp_reduction";
	public static float DP_REDUCTION = 0.2f;
	public static float DP_REDUCTION_MAX = 10f;
	public static float DP_REDUCTION_MAX_DYN = 10f;
	public static boolean USE_DP_REDUCTION_SCALING = false;
	
	public static boolean isNoOfficer(MutableShipStatsAPI stats) {
		if (stats.getEntity() instanceof ShipAPI) {
			ShipAPI ship = (ShipAPI) stats.getEntity();
//			if (ship == Global.getCombatEngine().getShipPlayerIsTransferringCommandFrom()) {
//				return false; // player is transferring command, no bonus until the shuttle is done flying
//				// issue: won't get called again when transfer finishes
//			}
			return ship.getCaptain().isDefault();
		} else {
			FleetMemberAPI member = stats.getFleetMember();
			if (member == null) return true;
			return member.getCaptain().isDefault();
		}
	}
	
	public static boolean isOriginalNoOfficer(MutableShipStatsAPI stats) {
		if (stats.getEntity() instanceof ShipAPI) {
			ShipAPI ship = (ShipAPI) stats.getEntity();
//			if (ship == Global.getCombatEngine().getShipPlayerIsTransferringCommandFrom()) {
//				return false; // player is transferring command, no bonus until the shuttle is done flying
//			}
			return ship.getOriginalCaptain() != null && ship.getOriginalCaptain().isDefault();
		} else {
			FleetMemberAPI member = stats.getFleetMember();
			if (member == null) return true;
			return member.getCaptain().isDefault();
		}
	}
	
	public static void recalcDPReductionCap() {
		DP_REDUCTION_MAX_DYN = DP_REDUCTION_MAX;
		if (USE_DP_REDUCTION_SCALING) {
			DP_REDUCTION_MAX_DYN = (DP_REDUCTION_MAX * ((float)Global.getSettings().getBattleSize() / 400f));
		}
		return;
	}
	
	public static class Level1 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			if (isNoOfficer(stats)) {
				if (USE_HELM_BONUS) {
					new CaptainsHelmsmanship.Level1().apply(stats, hullSize, id, level);
					new CaptainsHelmsmanship.Level2().apply(stats, hullSize, id, level);
				}
				if (USE_DAMCON_BONUS) {
					new CaptainsDamageControl.Level2().apply(stats, hullSize, id, level);
					new CaptainsDamageControl.Level3().apply(stats, hullSize, id, level);
					new CaptainsDamageControl.Level4().apply(stats, hullSize, id, level);
				}
				if (USE_ORDNANCE_BONUS) {
					new CaptainsOrdnanceExpertise.Level1().apply(stats, hullSize, id, level);
				}
				
				if (USE_ENDURANCE_BONUS) {
					new CaptainsCombatEndurance.Level1B().apply(stats, hullSize, id, level);
					new CaptainsCombatEndurance.Level2B().apply(stats, hullSize, id, level);
					new CaptainsCombatEndurance.Level3B().apply(stats, hullSize, id, level);
					new CaptainsCombatEndurance.Level5B().apply(stats, hullSize, id, level);
				}
			} 
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			if (USE_HELM_BONUS) {
				new CaptainsHelmsmanship.Level1().unapply(stats, hullSize, id);
				new CaptainsHelmsmanship.Level2().unapply(stats, hullSize, id);
			}
			if (USE_DAMCON_BONUS) {
				new CaptainsDamageControl.Level2().unapply(stats, hullSize, id);
				new CaptainsDamageControl.Level3().unapply(stats, hullSize, id);
				new CaptainsDamageControl.Level4().unapply(stats, hullSize, id);
			}
			if (USE_ORDNANCE_BONUS) { new CaptainsOrdnanceExpertise.Level1().unapply(stats, hullSize, id); }
			
			if (USE_ENDURANCE_BONUS) {
				new CaptainsCombatEndurance.Level1B().unapply(stats, hullSize, id);
				new CaptainsCombatEndurance.Level2B().unapply(stats, hullSize, id);
				new CaptainsCombatEndurance.Level3B().unapply(stats, hullSize, id);
				new CaptainsCombatEndurance.Level5B().unapply(stats, hullSize, id);
			}
		}
		
		public String getEffectDescription(float level) {
			String desc = "获得基础的";
			int nSkills = 0;
			if (USE_HELM_BONUS) {
				nSkills++;
				desc += " 操舵技术";
			}
			if (USE_DAMCON_BONUS) {
				nSkills++;
				if (nSkills > 1) { desc += ","; }
				desc += " 损伤管制";
			}
			if (USE_ORDNANCE_BONUS) {
				nSkills++;
				if (nSkills > 1) { desc += ","; }
				if (nSkills > 2 && !USE_ENDURANCE_BONUS) { desc += " 和"; }
				desc += " 军械专长";
			}
			if (USE_ENDURANCE_BONUS) {
				nSkills++;
				if (nSkills > 1) { desc += ","; }
				if (nSkills > 2) { desc += " 以及"; }
				desc += " 战斗耐力(" + Math.round(CaptainsCombatEndurance.NO_OFFICER_MULT * 100f) + "%)";
			}
			if (nSkills == 0) { desc = ""; } else { desc += " 技能\n若舰船没有分派军官"; }
			
			return desc;
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
			recalcDPReductionCap();
			if (isNoOfficer(stats)) {
				float baseCost = stats.getSuppliesToRecover().getBaseValue();
				float reduction = Math.min(DP_REDUCTION_MAX_DYN, baseCost * DP_REDUCTION);
				
				if (stats.getFleetMember() == null || stats.getFleetMember().getVariant() == null || 
						(!stats.getFleetMember().getVariant().hasHullMod(HullMods.NEURAL_INTERFACE) &&
						 !stats.getFleetMember().getVariant().hasHullMod(HullMods.NEURAL_INTEGRATOR))
								) {
					stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MOD).modifyFlat(SUPPORT_DOCTRINE_DP_REDUCTION_ID, -reduction);
				}
			} 
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.DEPLOYMENT_POINTS_MOD).unmodifyFlat(SUPPORT_DOCTRINE_DP_REDUCTION_ID);
		}
		
		public String getEffectDescription(float level) {
			recalcDPReductionCap();
			String max = "" + (int) DP_REDUCTION_MAX_DYN;
			String percent = "" + (int)Math.round(DP_REDUCTION * 100f) + "%";
			return "部署点 -" + percent + " 或 " + max + " 点，按两者中较低者计算";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}	
}





