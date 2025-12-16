package second_in_command.skills.piracy

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class HuntingGrounds : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "所有护卫舰和驱逐舰"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+15%% 护卫舰和驱逐舰最高航速", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+10%% 护卫舰和驱逐舰机动性", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

        tooltip.addSpacer(10f)
        tooltip.addPara("影响：{地面行动", 0f, Misc.getGrayColor(), Misc.getBasePlayerColor(), "地面行动")
        tooltip.addSpacer(10f)

        tooltip.addPara("+30%% 突袭等地面行动的效果", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("-25%% 突袭等地面行动中陆战队的伤亡", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        if (hullSize == ShipAPI.HullSize.FRIGATE || hullSize == ShipAPI.HullSize.DESTROYER) {
            stats!!.maxSpeed.modifyPercent(id, 15f)
            stats!!.acceleration.modifyPercent(id, 10f)
            stats!!.deceleration.modifyPercent(id, 10f)
        }

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }

    override fun advance(data: SCData, amunt: Float?) {
        data.fleet.stats.dynamic.getMod(Stats.PLANETARY_OPERATIONS_MOD).modifyPercent("sc_improvised_raids", 30f, "临机突袭")
        data.fleet.stats.dynamic.getStat(Stats.PLANETARY_OPERATIONS_CASUALTIES_MULT).modifyMult("sc_improvised_raids", 0.75f, "临机突袭")
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.PLANETARY_OPERATIONS_MOD).modifyPercent("sc_improvised_raids", 30f, "临机突袭")
        data.fleet.stats.dynamic.getStat(Stats.PLANETARY_OPERATIONS_CASUALTIES_MULT).modifyMult("sc_improvised_raids", 0.75f, "临机突袭")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getMod(Stats.PLANETARY_OPERATIONS_MOD).unmodify("sc_improvised_raids")
        data.fleet.stats.dynamic.getStat(Stats.PLANETARY_OPERATIONS_CASUALTIES_MULT).unmodify("sc_improvised_raids")
    }
}