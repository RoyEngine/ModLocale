package second_in_command.skills.warfare

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class ImmovableObject : SCBaseSkillPlugin() {


    override fun getAffectsString(): String {
        return "舰队中所有舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+20%% 武器和引擎的修理速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+30%% 武器和引擎的耐久度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+100%% 舰船质量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 舰船质量主要用于{碰撞伤害}的计算", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "碰撞伤害")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

        stats!!.weaponHealthBonus.modifyPercent(id, 30f)
        stats!!.engineHealthBonus.modifyPercent(id, 30f)

        stats!!.combatEngineRepairTimeMult.modifyMult(id, 0.8f)
        stats!!.combatWeaponRepairTimeMult.modifyMult(id, 0.8f)

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI, variant: ShipVariantAPI, id: String?) {

        if (ship.customData.containsKey("sc_immoveable_object")) return
        ship.mass += ship.mass
        ship.setCustomData("sc_immoveable_object", true)

    }

    override fun onActivation(data: SCData) {

    }

    override fun onDeactivation(data: SCData) {

    }

}